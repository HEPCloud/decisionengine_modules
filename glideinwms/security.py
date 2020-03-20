#!/usr/bin/python

import os
import time
import calendar
from glideinwms.lib import x509Support
from glideinwms.lib import condorExe

import logging

logger = logging.getLogger()


class Credential:

    def __init__(self, proxy_id, proxy_fname, group_descript):
        self.req_idle = 0
        self.req_max_run = 0
        self.advertize = False

        proxy_security_classes = group_descript['ProxySecurityClasses']
        proxy_trust_domains = group_descript['ProxyTrustDomains']
        proxy_types = group_descript['ProxyTypes']
        proxy_keyfiles = group_descript['ProxyKeyFiles']
        proxy_pilotfiles = group_descript['ProxyPilotFiles']
        proxy_vm_ids = group_descript['ProxyVMIds']
        proxy_vm_types = group_descript['ProxyVMTypes']
        proxy_creation_scripts = group_descript['ProxyCreationScripts']
        proxy_update_frequency = group_descript['ProxyUpdateFrequency']
        proxy_vmid_fname = group_descript['ProxyVMIdFname']
        proxy_vmtype_fname = group_descript['ProxyVMTypeFname']
        proxy_remote_username = group_descript['ProxyRemoteUsernames']
        proxy_project_id = group_descript['ProxyProjectIds']
        self.proxy_id = proxy_id
        # self.filename (absfname) always contains component of credential
        # used to submit glidein and based on the type contains following:
        # grid_proxy: x509 proxy (also used by pilot to talk to User collector
        # key_pair: public/access key
        # cert_pair: public cert
        # auth_file: auth file used
        self.filename = proxy_fname
        self.type = proxy_types.get(proxy_fname, "Unknown")
        self.security_class = proxy_security_classes.get(proxy_fname, proxy_id)
        self.trust_domain = proxy_trust_domains.get(proxy_fname, "None")
        self.update_frequency = int(
            proxy_update_frequency.get(proxy_fname, -1))

        # Following items can be None
        self.vm_id_fname = proxy_vmid_fname.get(proxy_fname)
        self.vm_type_fname = proxy_vmtype_fname.get(proxy_fname)
        self.vm_id = proxy_vm_ids.get(proxy_fname)
        self.vm_type = proxy_vm_types.get(proxy_fname)
        self.creation_script = proxy_creation_scripts.get(proxy_fname)
        self.key_fname = proxy_keyfiles.get(proxy_fname)
        self.pilot_fname = proxy_pilotfiles.get(proxy_fname)
        self.remote_username = proxy_remote_username.get(proxy_fname)
        self.project_id = proxy_project_id.get(proxy_fname)

        # Will be initialized when get_id() is called
        self._id = None

    def get_id(self, recreate=False):
        """
        Generate the Credential id if we do not have one already
        Since the Id is dependent on the credential content for proxies
        recreate them if asked to do so

        :param recreate: Recreate the credential id
        :type recreate :obj: `Boolean`

        @rtype: string
        @return: Id of the credential
        """

        if (not self._id) or recreate:
            # Create the credential id
            self.create()
            self._id = self.file_id(self.get_id_filename())
        return self._id

    def get_id_filename(self):
        """
        Get credential file used to generate the credential id

        @rtype: string
        @return: credential filename used to create the credential id
        """

        cred_file = None
        if self.filename:
            cred_file = self.filename
        elif self.key_fname:
            cred_file = self.key_fname
        elif self.pilot_fname:
            cred_file = self.pilot_fname
        return cred_file

    def create(self):
        """
        Generate the credential
        """

        if self.creation_script:
            logger.debug("Creating credential using %s" %
                         (self.creation_script))
            try:
                condorExe.iexe_cmd(self.creation_script)
            except Exception as e:
                logger.exception(
                    "Creating credential using %s failed" % (self.creation_script))
                self.advertize = False

            # Recreating the credential can result in ID change
            self._id = self.file_id(self.get_id_filename())

    def create_if_not_exist(self):
        """
        Generate the credential if it does not exists.
        """

        if self.filename and (not os.path.exists(self.filename)):
            logger.debug("Credential %s does not exist." % (self.filename))
            self.create()

    def get_string(self, cred_file=None):
        """
        Based on the type of credentials read appropriate files and return
        the credentials to advertise as a string. The output should be
        encrypted by the caller as required.

        @rtype: string
        @return: Read the credential from the file and return the string
        """

        cred_data = ''
        if not cred_file:
            # If not file specified, assume the file used to generate Id
            cred_file = self.get_id_filename()
        try:
            data_fd = open(cred_file)
            cred_data = data_fd.read()
            data_fd.close()
        except Exception as e:
            # This credential should not be advertised
            self.advertize = False
            logger.exception("Failed to read credential %s: " % cred_file)
            raise
        return cred_data

    # PM: Why are the usage details part of Credential Class?
    #     This is overloading the purpose of Credential Class

    def add_usage_details(self, req_idle=0, req_max_run=0):
        """
        Add usage details for this credential
        """
        self.req_idle = req_idle
        self.req_max_run = req_max_run

    def get_usage_details(self):
        """
        Return usage details for this credential
        """
        return (self.req_idle, self.req_max_run)

    def file_id(self, filename, ignoredn=False):
        """
        Generate hash for the credential id
        """
        if (("grid_proxy" in self.type) and not ignoredn):
            dn = x509Support.extract_DN(filename)
            hash_str = filename + dn
        else:
            hash_str = filename
        return str(abs(hash(hash_str)) % 1000000)

    def time_left(self):
        """
        Returns the time left if a grid proxy
        If missing, returns 0
        If not a grid proxy or other unidentified error, return -1
        """
        if (not os.path.exists(self.filename)):
            return 0

        if ("grid_proxy" in self.type) or ("cert_pair" in self.type):
            time_list = condorExe.iexe_cmd(
                "openssl x509 -in %s -noout -enddate" % self.filename)
            if "notAfter=" in time_list[0]:
                time_str = time_list[0].split("=")[1].strip()
                timeleft = calendar.timegm(time.strptime(
                    time_str, "%b %d %H:%M:%S %Y %Z")) - int(time.time())
            return timeleft
        else:
            return -1

    def renew(self):
        """
        Renews credential if time_left()<update_frequency
        Only works if type is grid_proxy or creation_script is provided
        """
        remaining = self.time_left()
        if ((remaining != -1) and (self.update_frequency != -1) and
                (remaining < self.update_frequency)):
            self.create()

    def supports_auth_method(self, auth_method):
        """
        Check if this credential has all the necessary info to support
        auth_method for a given factory entry
        """
        type_set = set(self.type.split('+'))
        am_set = set(auth_method.split('+'))
        return am_set.issubset(type_set)

    def __str__(self):
        output = ""
        output += "id = %s\n" % self.get_id()
        output += "proxy_id = %s\n" % self.proxy_id
        output += "req_idle = %s\n" % self.req_idle
        output += "req_max_run = %s\n" % self.req_max_run
        output += "filename = %s\n" % self.filename
        output += "type = %s\n" % self.type
        output += "security_class = %s\n" % self.security_class
        output += "trust_domain = %s\n" % self.trust_domain
        try:
            output += "key_fname = %s\n" % self.key_fname
            output += "pilot_fname = %s\n" % self.pilot_fname
        except Exception as e:
            pass
        output += "vm_id = %s\n" % self.vm_id
        output += "vm_type = %s\n" % self.vm_type
        output += "remote_username = %s\n" % self.remote_username
        output += "project_id = %s\n" % self.project_id

        return output


class CredentialCache:

    # Cache the credential ids so we do not create again unless required
    # Specially expensive to create id for proxy which uses DN in hash
    def __init__(self):
        self.file_id_cache = {}

    def file_id(self, cred, filename):
        """
        Return the cached credential id for the credential
        """

        k = (cred.type, filename)
        if not (k in self.file_id_cache):
            self.file_id_cache[k] = cred.file_id(filename)
        return self.file_id_cache[k]
