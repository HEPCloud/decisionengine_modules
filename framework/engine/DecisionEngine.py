#!/usr/bin/env python
"""
Main loop for Decision Engine.
The following environment variable points to decision engine configuration file:
``DECISION_ENGINE_CONFIG_FILE``
if this environment variable is not defined the ``DE-Config.py`` file from the ``../tests/etc/` directory will be used.
"""

import sys
import time
import threading
import logging
import os

import modules.de_logger as de_logger
import configmanager.ConfigManager as Conf_Manager
import taskmanager.TaskManager as TaskManager
import dataspace.datablock as datablock
import dataspace.dataspace as dataspace


CONFIG_UPDATE_PERIOD = 10 # seconds

class DecisionEngine(object):

    def __init__(self):
        self.logger = logging.getLogger("decision_engine")
        self.stop = threading.Event()
        self.stop_decision_maker = threading.Event()

    def get_logger(self):
        return self.logger

    def run(self, method, args=[]):
        """
        Create and start  new thread.

        :type args: :obj:`list`
        :arg args: arguments
        """

        thread = threading.Thread(group=None, target=method,
                              name=method, args=args)
        rc = True
        try:
            thread.start()
        except:
            exc, detail = sys.exc_info()[:2]
            self.logger.error("error starting thread %s: %s" % (name, detail))
            rc = False
        return rc

    def main(self):
        config_manager = Conf_Manager.ConfigManager()
        config_manager.load()
        global_config = config_manager.get_global_config()
        channels = config_manager.get_channels()

#        ds = dataspace.DataSpace("/tmp/test.db",None)     
#        ds.create()
#        taskmanager_id = 1
#        generation_id = 1
#        datablock = datablock.DataBlock(taskmanager_id, generation_id, ds)         
#
        task_managers = {} 
        data_space = {}
        """
        create channels
        """
        for ch in channels:
                task_managers[ch] = TaskManager.TaskManager(ch, channels[ch], datablock.DataBlock(ch, 0, data_space))
                
        for key, value in task_managers.iteritems():
            t = threading.Thread(target=value.run, args=(), name="Thread-%s"%(key,), kwargs={})
            t.start()


        try:
            while True: 
                time.sleep(10)
                if threading.activeCount() <= 1 : break
        except (SystemExit, KeyboardInterrupt):   
            pass


if __name__ == '__main__':
    de = DecisionEngine()
    de.main()
