#!/usr/bin/env/python
"""
Task Manager
"""


class Worker:
    def __init__(self, source_dict):
        name = source_dict['module']
        module = __import__('modules.%s'%(name,))
        m_class = getattr(getattr(module, name), name)
        self.worker = m_class(source_dict['parameters'], None)
        self.shedule = source_dict.get('shedule')
        self.run_counter = 0


'''
class Source:
    def __init__(self, source_dict):
        print "INIT SOURCE", source_dict
        name = source_dict['module']
        module = __import__('modules.%s'%(name,))

        print "MOD", module
        m_class = getattr(getattr(module, name), name)
        print "CLASS", m_class
        self.src = m_class(source_dict['parameters'], None)

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

class Channel:
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
class TaskManager:
    def __init__(self, channel_dict):
        self.channel = Channel(channel_dict)
        print "TM Channel", self.channel
        self.state = BOOT
        self.decision_cycle_active = False



    def do_backup(self):

    def run_source(self,
    def run_sources(self, data_block=None):
        if not data_block:
            return
        for s in self.channel.sources:
            self.channel.sources[s].worker.acquire(data_block)

    def run_transforms(self, data_block=None):
        if not data_block:
            return
        for t in self.channel.transforms:
            self.channel.transforms[t].worker.acquire(data_block)

    def run_logic_engine(self, data_block=None):
        if not data_block:
            return
        for le in self.channel.le_s:
            self.channel.le_s[le].worker.evaluate(data_block)

    def run_publishers(self, data_block=None):
        if not data_block:
            return
        for p in self.channel.publishers:
            self.channel.publishers[p].worker.publish(data_block)


    def boot(self):
        return
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



