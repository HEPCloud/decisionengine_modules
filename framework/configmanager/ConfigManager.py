import importlib
import os
import string

CONFIG_FILE_NAME = "decision_engine.conf"


class ConfigManager(object):

    def __init__(self):
        self.config_dir = os.getenv("CONFIG_PATH", "/etc/decisionengine")
        if not os.path.isdir(self.config_dir): 
            raise Exception("Config dir '%s' not found" % self.config_dir)
        self.config_file = os.path.join(self.config_dir, CONFIG_FILE_NAME)
        if not os.path.isfile(self.config_file): 
            raise Exception("Config file '%s' not found" % self.config_file)
        self.channel_config_dir = os.path.join(self.config_dir, "config.d")
        self.global_config = {}

    def load(self):
        self.last_update_time = os.stat(self.config_file).st_mtime
        code = None
        with open(self.config_file, "r") as f:
            code = "self.global_config=" + string.join(f.readlines(), "")
        if code: 
            exec(code)
        # load channels 
        self.channels = {}
        for direntry in os.listdir(self.channel_config_dir):
            name = direntry.split('.')[0]
            channel_conf = os.path.join(self.channel_config_dir, direntry)
            with open(os.path.abspath(channel_conf), "r") as f:
                code = "self.channels[name]=" + string.join(f.readlines(), "")
                exec(code)

    def is_updated(self):
        return 

    def get_channels(self):
        return self.channels

    def get_global_config(self):
        return self.global_config

    """
    Factory method:  create instance of dynamically loaded module 
    """
    @staticmethod
    def create(module_name, class_name, parameters):
        my_module = importlib.import_module(module_name)
        clazz = getattr(my_module, class_name)
        instance = clazz(parameters)
        return instance 


if __name__ == "__main__":
    c = ConfigManager()
    c.load()
