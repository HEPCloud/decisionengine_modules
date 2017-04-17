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

CONFIG_UPDATE_PERIOD = 10 # seconds

class DE:
    def __init__(self):
        self.logger = logging.getLogger("decision_engine")
        self.stop = threading.Event()
        self.stop_decision_maker = threading.Event()

    '''
    def components_monitor(self):
        """
        Monitors downloaded plugins.
        Sends alarm if a plugin stopped.
        """

        while True:
            threads = threading.enumerate() # get all alive threads
            thread_names = []
            for thread in threads:
                thread_names.append(thread.getName())
            names_to_remove = []
            for name in self.plugins:
                if name in thread_names:
                        self.logger.info("plugin %s is running"%(name,))
                else:
                    self.logger.critical("plugin %s is not running. Will remove from plugins"%(name,))
                    names_to_remove.append(name)
            for name in names_to_remove:
                del(de.plugins[name])
            if self.stop.wait(30):
                break
        self.stop_decision_maker.set()
    '''

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


if __name__ == '__main__':
    de = DE()
    config_manager = Conf_Manager.ConfigManager()
    config_manager.load()
    global_config = config_manager.get_global_config()
    channels = config_manager.get_channels()
    print "GLOBAL CONF", global_config
    print "CHANNELS", channels
    task_mgrs = {}
    for ch in channels:
        task_mgrs[ch] = TaskManager.TaskManager(channels[ch])


    while 1:
        for t_mgr in task_mgrs:
            task_mgrs[t_mgr].run()
        time.sleep(20)



    sys.exit(0)
    try:
        de_logger.set_logging(log_file_name = cm.config_dict['logger']['log_file'],
                              max_file_size = cm.config_dict['logger']['max_file_size'],
                              max_backup_count = cm.config_dict['logger']['max_backup_count'])
    except Exception, e:
        print e
        sys.exit(1)
    '''
    # Create and start plugins_monitor in a separate thread.
    started = de.run(de.plugins_monitor)
    if not started:
        sys.exit(1)
    '''
    while True:
        try:
            if cm.need_update():
                # Currently checks the configuration file m_time.
                # In the future the corresponding client command can be added.
                cm.read_config()
                # add plugin
                for plugin_name in cm.config_dict['plugins']:
                    if plugin_name not in de.plugins:
                       """
                       The plugins configuration is as follows:
                       'plugins': {<plugin unique name>: {'module':<module name>
                                                         'parameters': {main() method arguments}
                                                         }
                       So the same plugin module can be instantiated with different arguments.
                       """

                       # plugin controller
                       p = plugin.PluginControl(plugin_name, # name of plugin module
                                                cm.config_dict['plugins'])
                       p.load() # loads pertaining plugin onfiguration from the common configuration
                       p.run() # starts plugin and runs it a a loop in a separate thread.
                       de.plugins[plugin_name] = p

                # Stop plugin, removed from confiruration.
                # In current implementation you need to remove plugin from configuration.
                # if you either want to stop it running, or modify the plugin module.
                names_to_remove = []
                for plugin_name in de.plugins:
                    if plugin_name not in cm.config_dict['plugins']:
                        de.plugins[plugin_name].stop()
                        names_to_remove.append(plugin_name)
                for name in names_to_remove:
                    del(de.plugins[name])

            time.sleep(CONFIG_UPDATE_PERIOD) # may do something else here
        except (SystemExit, KeyboardInterrupt):
            for p in de.plugins:
                de.plugins[p].stop()
            de.stop.set()
            break
    sys.exit(0)
