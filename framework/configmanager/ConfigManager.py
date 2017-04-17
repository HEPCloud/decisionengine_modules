import logging
import os
import string
import time

CONFIG_FILE_NAME="DE-Config.py"

class ConfigManager(object):
    def __init__(self):
        self.config_dir = os.getenv("CONFIG_PATH")
        if not self.config_dir or not os.path.isdir(self.config_dir) : 
            raise Exception("no config file")
        self.config_dir += "/decisionengine"
        self.channel_config_dir = os.path.join(self.config_dir,"config.d")

        self.config_file = os.path.join(self.config_dir,CONFIG_FILE_NAME)
        
        
    def load(self):
        self.last_update_time = os.stat(self.config_file).st_mtime
        code = None
        with open(self.config_file,"r") as f:
            code = "self.global_config="+string.join(f.readlines(),"")
        if code : 
            exec(code)
        # load channels 
        self.channels = {}
        for direntry in os.listdir(self.channel_config_dir):
            name = direntry.split('.')[0]
            with open(os.path.abspath(os.path.join(self.channel_config_dir,direntry)),"r") as f:
                code="self.channels[name] ="+string.join(f.readlines(),"")
                exec(code)

    def get_channels(self):
        return self.channels

    def get_global_config(self):
        return self.global_config
    

if __name__ == "__main__":
    c = ConfigManager()
    c.load()
            
