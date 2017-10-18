#!/usr/bin/env python
"""
Main loop for Decision Engine.
The following environment variable points to decision engine configuration file:
``DECISION_ENGINE_CONFIG_FILE``
if this environment variable is not defined the ``DE-Config.py`` file from the ``../tests/etc/` directory will be used.
"""

import logging
import signal
import sys
import multiprocessing
import uuid

import SocketServer
import SimpleXMLRPCServer

import decisionengine.framework.modules.de_logger as de_logger
import decisionengine.framework.configmanager.ConfigManager as Conf_Manager
import decisionengine.framework.taskmanager.TaskManager as TaskManager

import decisionengine.framework.dataspace.datablock as datablock
import decisionengine.framework.dataspace.dataspace as dataspace


CONFIG_UPDATE_PERIOD = 10  # seconds


class Worker(multiprocessing.Process):

    def __init__(self, task_manager):
        super(Worker, self).__init__()
        self.task_manager = task_manager

    def run(self):
        self.task_manager.run()


class RequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class RpcServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
    def __init__(self, server_address, RequestHandlerClass):
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, server_address,
                                    requestHandler=RequestHandlerClass)


class DecisionEngine(SocketServer.ThreadingMixIn,
                     SimpleXMLRPCServer.SimpleXMLRPCServer):

    def __init__(self, cfg, server_address, RequestHandlerClass):
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self,
                                                       server_address,
                                                       logRequests=False,
                                                       requestHandler=RequestHandlerClass)

        self.logger = logging.getLogger("decision_engine")
        signal.signal(signal.SIGHUP, self.handle_sighup)
        self.task_managers = {}
        self.config_manager = cfg
        self.dataspace = dataspace.DataSpace(self.config_manager.get_global_config())

    def get_logger(self):
        return self.logger

    def _dispatch(self, method, params):
        try:
            """
            methods allowed to be executed by rpc
            have rpc pre-pended
            """
            func = getattr(self, "rpc_" + method)
        except AttributeError:
            raise Exception('method "%s" is not supported' % method)
        else:
            return func(*params)

    def rpc_show_config(self, channel=None):
        """

        :type channel: string
        """
        if not channel:
            return self.config_manager.get_channels()
        else:
            return self.config_manager.get_channels()[channel]

    def rpc_status(self):
        width =  max(map(lambda x: len(x), self.task_managers.keys())) + 1
        txt=""
        for ch, worker in self.task_managers.items():
            txt += "channel: {:<{width}}, id = {:<{width}}, state = {:<10} \n".format(ch,worker.task_manager.id ,TaskManager._state_names[worker.task_manager.get_state()],width=width)
        return txt[:-1]

    def rpc_stop(self):
        for ch, worker in self.task_managers.items():
            worker.terminate()
        self.shutdown()
        return "OK"

    def rpc_start_channel(self, channel):
        if channel in self.task_managers:
            return "ERROR, channel {} is running".format(channel)
        self.start_channel(channel)
        return "OK"

    def start_channel(self, channel):
        ch = self.config_manager.get_channels()[channel]
        generation_id = 1
        task_manager = TaskManager.TaskManager(channel,
                                               ch,
                                               datablock.DataBlock(self.dataspace,
                                                                   str(uuid.uuid4()).upper(),
                                                                   generation_id))
        worker = Worker(task_manager)
        self.task_managers[channel] = worker
        worker.start()

    def rpc_start_channels(self):
        self.start_channels()
        return "OK"

    def start_channels(self):
        channels = self.config_manager.get_channels()
        if not channels:
            raise RuntimeError("No channels configured")
        """
        start channels
        """
        for ch in channels:
            self.start_channel(ch)

    def rpc_stop_channel(self,channel):
        self.stop_channel(channel)
        return "OK"

    def stop_channel(self,channel):
        print channel, self.task_managers
        worker = self.task_managers[channel]
        print "Worker", worker
        worker.terminate()
        del self.task_managers[channel]

    def rpc_stop_channels(self):
        self.stop_channels()
        return "OK"

    def stop_channels(self):
        channels = self.task_managers.keys()
        for ch in channels:
            self.stop_channel(ch)

    def handle_sighup(self, signum,frame):
        self.stop_channels()
        self.reload_config()
        self.start_channels()

    def rpc_reload_config(self):
        self.reload_config()
        return "OK"

    def reload_config(self):
        self.config_manager.reload()

if __name__ == '__main__':
    try:
        conf_manager = Conf_Manager.ConfigManager()
        conf_manager.load()
        channels = conf_manager.get_channels()

        if not channels:
            raise RuntimeError("No channels configured")

        global_config = conf_manager.get_global_config()
        server_address = global_config.get("server_address",("localhost", 8888))

        server = DecisionEngine(conf_manager,
                                server_address,
                                RequestHandler)
        server.start_channels()
        server.serve_forever()

    except Exception, msg:
        sys.stderr.write("Fatal Error: {}\n".format(msg))
        sys.exit(1)

