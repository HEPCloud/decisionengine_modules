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

import decisionengine.framework.modules.de_logger as de_logger
import decisionengine.framework.configmanager.ConfigManager as Conf_Manager
import decisionengine.framework.taskmanager.TaskManager as TaskManager

import decisionengine.framework.dataspace.datablock as datablock
import decisionengine.framework.dataspace.dataspace as dataspace


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

        # TODO: Make sure log rotation is threadsafe
        logfile = global_config['logger']['log_file']
        logfile_size = global_config['logger'].get('max_file_size', 10000000)
        logfile_backup_count = global_config['logger'].get('max_backup_count', 5)
        #formatter = logging.Formatter("%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s")
        #handler = logging.handlers.RotatingFileHandler(
        #    logfile, maxBytes=logfile_size, backupCount=logfile_backup_count)
        #handler.setFormatter(formatter)
        #self.logger.addHandler(handler)
        #self.logger.setLevel(logging.INFO)
        self.logger = de_logger.set_logging(
            log_file_name=logfile, max_file_size=logfile_size,
            max_backup_count=logfile_backup_count)

        ds = dataspace.DataSpace(global_config)
        taskmanager_id = 1
        generation_id = 1

        task_managers = {} 
        data_space = {}
        """
        create channels
        """
        for ch in channels:
                task_managers[ch] = TaskManager.TaskManager(ch, channels[ch], datablock.DataBlock(ds,taskmanager_id, generation_id))
                
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
