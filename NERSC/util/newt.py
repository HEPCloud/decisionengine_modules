"""
Newt API interface
"""

from copy import deepcopy
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

"""
Newt base URL. When not specified in constructor this
URL will be used.
"""
_NEWT_BASE_URL = "https://newt.nersc.gov/newt/"


class Newt(object):

    def __init__(self, password_file, newt_base_url=None, num_retries=0,
                 retry_backoff_factor=0):
        """
        Constructor that takes path to password file and
        optional Newt base URL
        :param password_file: path to password file
        :param newt_base_url: Newt base URL (default will be _NEWT_BASE_URL)
        """
        if not password_file:
            raise RuntimeError("No password file specified")
        if not os.path.exists(password_file):
            raise RuntimeError("password file '{}' does not exist".
                               format(password_file))
        self.password_file = password_file
        self.newt_base_url = newt_base_url if newt_base_url else _NEWT_BASE_URL
        if not self.newt_base_url.endswith("/"):
            self.newt_base_url += "/"
        self.session = requests.Session()
        self.num_retries = num_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.expiration_time = time.time()
        self._add_retries_to_session()

    def _add_retries_to_session(self):
        """
        Adds retries to requests Session for requests to NEWT URLs
        :return: void
        """
        retry = Retry(
            status=self.num_retries,
            status_forcelist=[500, ],
            backoff_factor=self.retry_backoff_factor,
            method_whitelist=False)
        retry_adapter = HTTPAdapter(max_retries=retry)
        self.session.mount(self.newt_base_url, retry_adapter)

    def _login(self):
        """
        Establishes newt Session
        :return: void
        """
        if self.expiration_time < time.time() + 3600:
            login_url = self.newt_base_url + "login/"
            postfields = None
            with open(self.password_file) as f:
                postfields = "&".join([line[:-1].strip()
                                       for line in f.readlines()])

            r = self.session.post(login_url, data=postfields)
            r.raise_for_status()
            response_dict = r.json()
            if not response_dict.get("auth"):
                raise RuntimeError(
                    "Failed to establish session to {}".format(login_url))
            self.expiration_time = response_dict.get(
                'session_lifetime') + time.time()

    def get_usage(self, username):
        """
        Returns allocation and usage for the given user using NEWT IRIS API
        :param username: string username
        :return: json containing allocation and usage information for a given user
        """
        self._login()
        iris_url = "{}/{}".format(self.newt_base_url, 'account/iris')
        query = (
            "accounts(username: \\\"{}\\\") {{ "
            "   projectId, "
            "   repoName, "
            "   repoType, "
            "   currentAlloc, "
            "   usedAlloc, "
            "   users {{ "
            "       uid, "
            "       name, "
            "       firstname, "
            "       lastname, "
            "       middlename, "
            "       userAlloc, "
            "       userAllocPct, "
            "       usedAlloc "
            "   }} "
            "}}"
        ).format(username)
        # Remove whitespace to make more readable
        query = query.replace(" ", "").replace(",", ", ")
        r = self.session.post(
            url=iris_url,
            data={"query": query})
        r.raise_for_status()
        raw_json = r.json()

        # Flatten json so it returns data that follows the old NEWT structure
        final = {'items': []}
        for account in raw_json['data']['newt']['accounts']:
            _item = {k: v for k, v in account.items() if k != 'users'}
            for user in account['users']:
                _item2 = deepcopy(_item)
                _item2.update(user)
                final['items'].append(_item2)
        return final

    def get_status(self, system=None):
        """
        Returns system status for a given system (if provided) or all systems
        :param system: string name of the system (optional)
        :return: json containing system status
        """
        self._login()
        status_url = self.newt_base_url + "status/"
        if system:
            status_url += system
        r = self.session.get(status_url)
        r.raise_for_status()
        return r.json()

    def get_queue(self, system, query=None):
        """
        Returns information about queues controlled by
        optional query name parameter
        :param system: string system name (like 'cori', 'edison' ..)
        :param query: string query (optional)
        :return: json containing queue information
        """
        self._login()
        queue_url = self.newt_base_url + "queue/" + system + "/"
        if query:
            queue_url += query
        r = self.session.get(queue_url)
        r.raise_for_status()
        return r.json()
