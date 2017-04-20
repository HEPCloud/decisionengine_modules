#!/usr/bin/env/python
"""
Task Manager
"""
import threading
import logging
import time
import sys
import types

import decisionengine.framework.dataspace.datablock as datablock
import decisionengine.framework.configmanager.ConfigManager as configmanager
import decisionengine.framework.modules.de_logger as de_logger

class Worker(object):
    def __init__(self, source_dict):
        self.worker = configmanager.ConfigManager.create(source_dict['module'],
                                                         source_dict['parameters'])
        self.module = source_dict['module']
        self.name = self.worker.__class__.__name__
        self.shedule = source_dict.get('shedule')
        self.run_counter = 0
        self.stop_running = threading.Event()
        self.data_updated = threading.Event()
'''
class Source(Worker):
    def __init__(self, source_dict, lock):
        Worker.__init__(source_dict)
        self.stop = False


class Transform:
    def __init__(self, source_dict):
        name = source_dict['module']
        modlule = __import__('modules.%s'%(name,))
        m_class = getattr(getattr(module, name), name)
        self.transform = m_class(source_dict['parameters'], None)
class LogicEngine:
    def __init__(self, source_dict):
        name = source_dict['module']
        modlule = __import__(source_dict['module'])
        m_class = getattr(getattr(name, module), name)
        self.le = m_class(source_dict['parameters'], None)
class Publisher:
    def __init__(self, source_dict):

        modlule = __import__(source_dict['module'])
        m_class = getattr(module, source_dict['module'])
        self.publisher = m_class(source_dict['parameters'], None)
'''

class Channel(object):
    def __init__(self, channel_dict):
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
    def __init__(self, task_manager_id, channel_dict, data_block):
        self.data_block_t0 = data_block # my current data block
        self.id = task_manager_id
        self.channel = Channel(channel_dict)
        print "TM Channel", self.channel
        self.state = BOOT
        self.decision_cycle_active = False
        self.lock = threading.Lock()
        self.logger = logging.getLogger("decision_engine")
        self.logger.info("TM starting %s" % (self.id,))
        self.stop_running = threading.Event()

    
    def wait_for_all_sources_ran(self, events_done):
        self.logger.info("Waiting for all sorces to run")
        e_done = events_done
        neevents = len(e_done)
        while not all([e.isSet() for e in events_done]):
            time.sleep(1)
            """
            ev_wait = [e.wait(1) for e in events_done])
            if all(ev_wait):
                
            evs = [e.is_set() for e in events_done]
            if all(evs):
                break
            """
        for e in events_done:
            e.clear()

    def wait_for_any_source_ran(self, events_done):
        while not any([e.isSet() for e in events_done]):
            time.sleep(1)
        for e in events_done:
            if e.isSet():
                e.clear()

    def run(self):
        '''
        Task Manager main loop
        '''

        done_events = self.start_sources(self.data_block_t0)
        # This is a boot phase
        # Wait until all sources run at least one time
        self.wait_for_all_sources_ran(done_events)
        self.logger.info("All sorces finished")
        self.decision_cycle()
        self.state = STEADY

        while self.state == STEADY:
            self.wait_for_any_source_ran(done_events)
            self.decision_cycle()
            self.sleep(1)

        """
        self.stop_running = args
        self.running.value = 1
        self.time_started = time.time()
        while self.running.value:
            self.idle = False
            with self.lock:
                try:
                    self.task.main(self.kwargs)
                except Exception, e:
                    exc, value, tb = sys.exc_info()
                    self.logger.error("run_forever:%s %s" % (self.name, str(e)))
                    for l in traceback.format_exception( exc, value, tb ):
                        self.logger.error("Traceback: %s"%(l,))
                    break
            self.logger.info("checking event %s"%(self.stop_running,))
            s = self.stop_running.wait(self.sleeptime)
            #s = stop_running.wait(self.sleeptime)
            if s:
                self.logger.info("received stop_running signal")
                break
        self.logger.info("stopped %s" % (self.name,))

        """
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
                self.logger.info('Src %s calling aquire'%(src.name,))
                data = src.worker.acquire()
                self.logger.info('Src %s aquire retuned %s'%(src.name, data))
                
                self.logger.info('Src %s filling header'%(src.name,))
                header = datablock.Header(self.data_block_t0.taskmanager_id, 
                                          create_time=time.time(), creator=src.module)
                self.logger.info('Src %s header done'%(src.name,))
                self.data_block_put(data, header, self.data_block_t0)
                self.logger.info('Src %s header put done'%(src.name,))
                src.run_counter += 1
                src.data_updated.set()
                self.logger.info('Src %s %s finished cycle'%(src.name, src.module))
            except Exception:
                exc, detail = sys.exc_info()[:2]
                self.logger.error("error running source %s %s %s" % (src, exc, detail))
            s = src.stop_running.wait(src.shedule)
            if s:
                self.logger.info("received stop_running signal for %s"%(src.name,))
                break
        self.logger.info("stopped %s" % (src.name,))

    def start_sources(self, data_block=None):
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
                self.logger.error("error starting thread %s: %s" % (name, detail))
                self.state = OFFLINE
                break
        return event_list

    def run_transforms(self, data_block=None):
        self.logger.info('run_transforms: data block %s'%(data_block,))
        if not data_block:
            return
        for t in self.channel.transforms:
            self.logger.info('run transform %s'%(self.channel.transforms[t].name,))
            try:
                data = self.channel.transforms[t].worker.transform(data_block)
                self.logger.info('transform returned %s'%(data,))
                header = datablock.Header(data_block.taskmanager_id, 
                                          creator=self.channel.transforms[t].name)
                self.data_block_put(data, header, data_block)
                self.logger.info('tranform put data')
            except Exception, detail:
                self.logger.errorr('exception from %s: %s'%(self.channel.transforms[t].name, detail))

    def run_logic_engine(self, data_block=None):
        if not data_block:
            return
        for le in self.channel.le_s:

            self.logger.info('run logic engine %s %s'%(self.channel.le_s[le].name, data_block))
            self.channel.le_s[le].worker.evaluate(data_block)
            self.logger.info('run logic engine done')

    def run_publishers(self, data_block=None):
        if not data_block:
            return
        for p in self.channel.publishers:
            self.channel.publishers[p].worker.publish()


    def boot(self):
        return

    def run_forever(self):
        # start sources
        for s in self.channel.sources:
            print "Calling produces for", s
            self.channel.sources[s].worker.produces(None)
        for s in self.channel.sources:
            print "Calling  acquire for ", s
            self.channel.sources[s].worker.acquire()
        for s in self.channel.transforms:
            print "Calling  produces for ", s
            self.channel.transforms[s].worker.produces(None)

        for s in self.channel.le_s:
            print "Calling produces for", s
            self.channel.le_s[s].worker.evaluate()
        for s in self.channel.publishers:
            print "Calling  acquire for ", s
            self.channel.publishers[s].worker.publish()
    """
    def run(self):
        for s in self.channel.sources:
            print "Calling produces for", s
            try:
                self.channel.sources[s].worker.produces(None)
            except Exception, msg:
                print "busted ", msg, self.channel.sources[s].worker.__class__.__name__
        for s in self.channel.sources:
            print "Calling  acquire for ", s
            self.channel.sources[s].worker.acquire()
        for s in self.channel.transforms:
            print "Calling  produces for ", s
            self.channel.transforms[s].worker.produces(None)

        for s in self.channel.le_s:
            print "Calling produces for", s
            self.channel.le_s[s].worker.evaluate( self.data_block_t0 )
        for s in self.channel.publishers:
            print "Calling  acquire for ", s
            self.channel.publishers[s].worker.publish()
    """
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
    taskmanager_id = 1
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


"""
    def run(self):
        for s in self.channel.sources:
            print "Calling produces for", s
            self.channel.sources[s].worker.produces(None)
        for s in self.channel.sources:
            print "Calling  acquire for ", s
            self.channel.sources[s].worker.acquire()
        for s in self.channel.transforms:
            print "Calling  produces for ", s
            self.channel.transforms[s].worker.produces(None)

        for s in self.channel.le_s:
            print "Calling produces for", s
            self.channel.le_s[s].worker.evaluate()
        for s in self.channel.publishers:
            print "Calling  acquire for ", s
            self.channel.publishers[s].worker.publish()
"""
