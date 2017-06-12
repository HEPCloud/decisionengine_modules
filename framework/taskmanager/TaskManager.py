#!/usr/bin/env/python
"""
Task Manager
"""
import threading
import logging
import time
import sys
import types
import uuid

import decisionengine.framework.dataspace.datablock as datablock
import decisionengine.framework.configmanager.ConfigManager as configmanager
import decisionengine.framework.modules.de_logger as de_logger

class Worker(object):
    """
    Provides interface to loadable modules an events to sycronise
    execution
    """

    def __init__(self, conf_dict):
        """
        :type conf_dict: :obj:`dict`
        :arg conf_dict: configuration dictionary describing the worker
        """
        self.worker = configmanager.ConfigManager.create(conf_dict['module'],
                                                         conf_dict['name'],
                                                         conf_dict['parameters'])
        self.module = conf_dict['module']
        self.name = self.worker.__class__.__name__
        self.schedule = conf_dict.get('schedule')
        self.run_counter = 0
        self.data_updated = threading.Event()
        self.stop_running = threading.Event()
    
class Channel(object):
    """
    Decision Channel.
    Instantiates workers according to channel configuration
    """

    def __init__(self, channel_dict):
        """
        :type channel_dict: :obj:`dict`
        :arg channel_dict: channel configuration
        """

        self.sources = {}
        self.transforms = {}
        self.le_s = {}
        self.publishers = {}
        for s in channel_dict['sources']:
            self.sources[s] = Worker(channel_dict['sources'][s])
        for s in channel_dict['transforms']:
            self.transforms[s] = Worker(channel_dict['transforms'][s])

        for s in channel_dict['logicengines']:
            self.le_s[s] = Worker(channel_dict['logicengines'][s])

        for s in channel_dict['publishers']:
            self.publishers[s] = Worker(channel_dict['publishers'][s])


# states
BOOT, STEADY, OFFLINE, SHUTDOWN = range(4)
_state_names =  ['BOOT', 'STEADY', 'OFFLINE', 'SHUTDOWN']
class TaskManager(object):
    """
    Task Manager
    """

    def __init__(self, task_manager_id, channel_dict, data_block):
        """
        :type task_manager_id: :obj:`int`
        :arg task_manager_id: Task Manager id provided by caller
        :type channel_dict: :obj:`dict`
        :arg channel_dict: channel configuration
        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block
        """

        self.data_block_t0 = data_block # my current data block
        self.id = task_manager_id
        self.channel = Channel(channel_dict)
        self.state = BOOT
        self.decision_cycle_active = False
        self.lock = threading.Lock()
        #self.logger = logging.getLogger("decision_engine")
        self.logger = de_logger.get_logger()
        self.logger.info("TM starting %s" % (self.id,))
        self.stop = False # stop running all loops when this is True


    def wait_for_all(self, events_done):
        """
        Wait for all sources or transforms to finish

        :type events_done: :obj:`list`
        :arg events_done: list of events to wait for
        """

        self.logger.info("Waiting for all tasks to run")
        while not all([e.isSet() for e in events_done]):
            time.sleep(1)
            if self.stop:
                break
            """
            ev_wait = [e.wait(1) for e in events_done])
            if all(ev_wait):

            evs = [e.is_set() for e in events_done]
            if all(evs):
                break
            """
        for e in events_done:
            e.clear()

    def wait_for_any(self, events_done):
        """
        Wait for any sources to finish

        :type events_done: :obj:`list`
        :arg events_done: list of events to wait for
        """
        while not any([e.isSet() for e in events_done]):
            time.sleep(1)
            if self.stop:
                break

        for e in events_done:
            if e.isSet():
                e.clear()

    def run(self):
        """
        Task Manager main loop
        """

        self.logger.info("Starting Task Manager %s"%(self.id,))
        done_events = self.start_sources(self.data_block_t0)
        # This is a boot phase
        # Wait until all sources run at least one time
        self.wait_for_all(done_events)
        self.logger.info("All sorces finished")
        self.decision_cycle()
        if self.state != OFFLINE:
            self.state = STEADY
        else:
            self.logger.error("Error occured. Task Manager %s exits"%(self.id,))
            return

        while self.state == STEADY:
            self.wait_for_any(done_events)
            self.decision_cycle()
            if self.stop:
                self.logger.info("Task Manager %s received stop signal and exits"%(self.id,))
                for s in self.channel.sources:
                    self.channel.sources[s].stop_running.set()
                    time.sleep(5)
                for t in self.channel.transforms:
                    self.channel.transforms[t].stop_running.set()
                    time.sleep(5)
                break

            time.sleep(1)
        self.logger.error("Error occured. Task Manager %s exits"%(self.id,))


    def stop_task_manager(self):
        """
        signal task manager to stop
        """
        self.stop = True

    def data_block_put(self, data, header, data_block):
        """
        Put data into data block

        :type data: :obj:`dict`
        :arg data: key, value pairs
        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block
        """

        if type(data) != types.DictType:
            self.logger.error('data_block put expecting %s type, got %s'%
                              (types.DictType, type(data)))
            return
        self.logger.info('data_block_put %s'%(data,))
        with data_block.lock:
            for k in data:
                data_block.put(k, data[k], header)

    def do_backup(self):
        """
        Duplicate current data block and return its copy

        :rtype: :obj:`~datablock.DataBlock`

        """

        with self.lock:
            data_block = self.data_block_t0.duplicate()
            self.logger.info('Duplicated block %s'%(data_block,))
        return data_block

    def decision_cycle(self):
        """
        Decision cycle to be run periodically (by trigger)
        """

        data_block_t1 = self.do_backup()
        try:
            self.run_transforms(data_block_t1)
        except Exception:
            exc, detail = sys.exc_info()[:2]
            self.logger.error("error in decision cycle(transforms) %s %s" % (exc, detail))
        try:
            self.run_logic_engine(data_block_t1)
        except Exception:
            exc, detail = sys.exc_info()[:2]
            self.logger.error("error in decision cycle(logic engine) %s %s" % (exc, detail))
        try:
            self.run_publishers(data_block_t1)
        except Exception:
            exc, detail = sys.exc_info()[:2]
            self.logger.error("error in decision cycle (publishers) %s %s" % (exc, detail))


    def run_source(self, src):
        """
        Get the data from source
        and put it into the data block

        :type src: :obj:`~Worker`
        :arg src: source Worker
        """

        while 1:
            try:
                self.logger.info('Src %s calling acquire'%(src.name,))
                data = src.worker.acquire()
                self.logger.info('Src %s acquire retuned %s'%(src.name, data))
                self.logger.info('Src %s filling header'%(src.name,))
                header = datablock.Header(self.data_block_t0.taskmanager_id,
                                          create_time=time.time(), creator=src.module)
                self.logger.info('Src %s header done'%(src.name,))
                self.data_block_put(data, header, self.data_block_t0)
                self.logger.info('Src %s data block put done'%(src.name,))
                src.run_counter += 1
                src.data_updated.set()
                self.logger.info('Src %s %s finished cycle'%(src.name, src.module))
            except Exception:
                exc, detail = sys.exc_info()[:2]
                self.logger.error("error running source %s %s %s" % (src.name, exc, detail))
            s = src.stop_running.wait(src.schedule)
            if s:
                self.logger.info("received stop_running signal for %s"%(src.name,))
                break
        self.logger.info("stopped %s" % (src.name,))

    def start_sources(self, data_block=None):
        """
        Start sources, each in a separate thread

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block
        """

        event_list = []
        for s in self.channel.sources:
            self.logger.info("starting loop for %s" % (s,))
            event_list.append(self.channel.sources[s].data_updated)
            thread = threading.Thread(group=None, target=self.run_source,
                                      name=self.channel.sources[s].name, args=([self.channel.sources[s]]), kwargs={})
            try:
                thread.start()
            except:
                exc, detail = sys.exc_info()[:2]
                self.logger.error("error starting thread %s: %s" % (self.channel.sources[s].name, detail))
                self.state = OFFLINE
                break
        return event_list

    def run_transforms(self, data_block=None):
        """
        Run transforms.
        So far in main process.

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block

        """
        self.logger.info('run_transforms: data block %s'%(data_block,))
        if not data_block:
            return
        event_list = []
        for t in self.channel.transforms:
            self.logger.info('starting transform %s'%(self.channel.transforms[t].name,))
            event_list.append(self.channel.transforms[t].data_updated)
            thread = threading.Thread(group=None, target=self.run_transform,
                                      name=self.channel.transforms[t].name, args=(self.channel.transforms[t], data_block), kwargs={})

            try:
                thread.start()
            except:
                exc, detail = sys.exc_info()[:2]
                self.logger.error("error starting thread %s: %s" % (self.channel.transforms[t].name, detail))
                self.state = OFFLINE
                break
                self.logger.error('exception from %s: %s'%(self.channel.transforms[t].name, detail))

        print "EVENT LIST", event_list
        self.wait_for_all(event_list)
        self.logger.info("all tranforms finished")
                
        
    def run_transform(self, transform, data_block):
        """
        Run a transform
        
        :type transform: :obj:`~Worker`
        :arg transform: source Worker
        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block
        """
        DATA_TO = 60
        consume_keys = transform.worker.consumes()
        
        self.logger.info('transform: %s expected keys: %s provided keys: %s'%(transform.name, consume_keys, data_block.keys()))
        loop_counter = 0
        while 1:
            with data_block.lock:
                # Check if data is ready
                if consume_keys in data_block.keys():
                    # data is ready -  may run transform()
                    self.logger.info('run transform %s'%(transform.name,))
                    try:
                        data = transform.worker.transform(data_block)
                        self.logger.info('transform returned %s'%(data,))
                        header = datablock.Header(data_block.taskmanager_id,
                                                  creator=transform.name)
                        self.data_block_put(data, header, data_block)
                        self.logger.info('tranform put data')
                    except Exception, detail:
                        self.logger.error('exception from %s: %s'%(self.channel.transforms[t].name, detail))
                    break
                else:
                    s = transform.stop_running.wait(1)
                    if s:
                        self.logger.info("received stop_running signal for %s"%(transform.name,))
                        break
                    loop_counter += 1
                    if loop_counter == DATA_TO:
                        self.logger.info("transform %s did not get consumes data in %s seconds. Exiting"%(transform.name, DATA_TO))
                        break
        transform.data_updated.set()

    def run_logic_engine(self, data_block=None):
        """
        Run Logic Engine.

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block
        """
        if not data_block:
            return
        for le in self.channel.le_s:

            self.logger.info('run logic engine %s %s'%(self.channel.le_s[le].name, data_block))
            self.channel.le_s[le].worker.evaluate(data_block)
            self.logger.info('run logic engine done')

    def run_publishers(self, data_block=None):
        """
        Run Publishers in main process.

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block

        """
        if not data_block:
            return
        for p in self.channel.publishers:
            self.logger.info('run publisher %s %s'%(self.channel.publishers[p].name, data_block))
            self.channel.publishers[p].worker.publish()



if __name__ == '__main__':
    import decisionengine.framework.dataspace.dataspace as dataspace

    config_manager = configmanager.ConfigManager()
    config_manager.load()
    global_config = config_manager.get_global_config()
    print "GLOBAL CONF", global_config

    my_logger = logging.getLogger("decision_engine")

    try:
        de_logger.set_logging(log_file_name = global_config['logger']['log_file'],
                              max_file_size = global_config['logger']['max_file_size'],
                              max_backup_count = global_config['logger']['max_backup_count'])
    except Exception, e:
        print e
        sys.exit(1)

    my_logger.info("Starting decision engine")


    channels = config_manager.get_channels()

    ds = dataspace.DataSpace(global_config)
    taskmanager_id = str(uuid.uuid4()).upper()
    generation_id = 1

    task_managers = {}
    data_space = {}
    """
    create channels
    """
    for ch in channels:
        task_managers[ch] = TaskManager(ch, channels[ch], datablock.DataBlock(ds,taskmanager_id, generation_id))

    for key, value in task_managers.iteritems():
        t = threading.Thread(target=value.run, args=(), name="Thread-%s"%(key,), kwargs={})
        t.start()

    try:
        while True:
            time.sleep(10)
            if threading.activeCount() <= 1 : break
    except (SystemExit, KeyboardInterrupt):
        pass
