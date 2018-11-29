"""
Newt API interface
"""


import json
import logging
import os
import time
import requests

NEWT_BASE_URL = "https://newt.nersc.gov/newt/"

class Newt(object):

    def __init__(self, password_file, newt_base_url = None):
        if not password_file:
            raise RuntimeError("No password file specified")
        if not os.path.exists(password_file):
            raise RuntimeError("password file '{}' does not exist".
                               format(password_file))
        self.password_file = password_file
        self.newt_base_url = newt_base_url if newt_base_url else NEWT_BASE_URL
        if not self.newt_base_url.endswith("/"):
            self.newt_base_url += "/"
        self.session = requests.Session()
        self.expiration_time = time.time()

    def login(self):
        if self.expiration_time < time.time() + 3600:
            login_url = self.newt_base_url + "login/"
            postfields = None
            with open(self.password_file) as f:
                postfields = "&".join([line[:-1].strip() for line in f.readlines()])
            r = self.session.post(login_url, data=postfields)
            r.raise_for_status()
            response_dict = r.json()
            if not response_dict.get("auth"):
                raise RuntimeError("Failed to establish session to {}".format(login_url))
            self.expiration_time  = response_dict.get('session_lifetime') + time.time()

    def get_usage(self, username):
        if self.expiration_time < time.time() + 3600:
            self.login()
        user_url = self.newt_base_url + "account/usage/user/" + username
        r = self.session.get(user_url)
        r.raise_for_status()
        return r.json()

    def get_status(self, system = None):
        if self.expiration_time < time.time() + 3600:
            self.login()
        status_url = self.newt_base_url + "status/"
        if system:
            status_url += system
        r = self.session.get(status_url)
        r.raise_for_status()
        return r.json()

    def get_queue(self, system, query=None):
        if self.expiration_time < time.time() + 3600:
            self.login()
        queue_url = self.newt_base_url + "queue/"  + system + "/"
        if query:
            queue_url += query
        r = self.session.get(queue_url)
        r.raise_for_status()
        return r.json()
