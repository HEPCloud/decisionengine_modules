# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Get allocation info from Nersc SuperFacilityAPI
"""
import json

# import time
import os

import jwt
import pandas as pd
import pem
import requests

# from decisionengine_modules.NERSC.util import newt
# from datetime import datetime
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc7523 import PrivateKeyJWT

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter


@Source.supports_config(Parameter("constraints", type=dict, comment="""Supports the layout:"""))
@Source.produces(Nersc_Allocation_SFAPI=pd.DataFrame)
class NerscSFApi(Source.Source):
    def __init__(self, config):
        super().__init__(config)

        self.constraints = config.get("constraints")
        if not isinstance(self.constraints, dict):
            raise RuntimeError("constraints should be a dict")

        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )
        self.localmap = {"uscms": "m2612", "fife": "m3249"}
        self.keys_list = ["hours_given", "hours_used", "id", "project_hours_given", "project_hours_used", "repo_name"]

    def check_accesstoken(self, nersc_user):
        # /etc/decisionengine/config.d/Nersc.jsonnet needs to also have
        # "token_url": "https://oidc.nersc.gov/c2id/token",
        token_url = self.constraints.get("token_url")

        # "NerscSFApi"in Nersc.jsonnet must contain constraints that has the following 2 dictionaries
        # "uscms": {
        #     "private_key":"/etc/decisionengine/modules.data/ucms_privkey.pem",
        #     "client_id_file":"/etc/decisionengine/modules.data/ucms_clientid.txt",
        #     "rawfile":"/tmp/ucms_access.token"
        # },
        # "fife": {
        #     "private_key":"/etc/decisionengine/modules.data/fife_privkey.pem",
        #     "client_id_file":"/etc/decisionengine/modules.data/fife_clientid.txt",
        #     "rawfile":"/tmp/fife_access.token"
        # }

        # nersc_user should be either "uscms" or "fife"
        try:
            params_dict = self.constraints[nersc_user]
        except KeyError:
            self.logger.error(f"Unknown user '{nersc_user}', exiting")
            return None
            
        rawfile = params_dict["rawfile"]
        pemfile = params_dict["private_key"]
        clientidfile = params_dict["client_id_file"]
        with open(clientidfile) as cifile:
            client_id = cifile.read()
            client_id = client_id.rstrip()

        if not os.path.exists(rawfile):
            self.logger.debug(f"{rawfile} does not exist. Need to generate")
        else:
            atoken = None
            with open(rawfile) as afile:
                atoken = afile.read()
                atoken = atoken.rstrip()
            # HK> If the access token is expired, the flow goes directly to except jwt.ExpiredSignatureError
            try:
                jwt.decode(atoken, options={"verify_signature": False})
                self.logger.debug("Access Token not expired. Returning without generating a new access token")
                return atoken  # This means the existing access token is not expired.

            except jwt.ExpiredSignatureError:
                self.logger.debug("Access Token expired")

        certs = pem.parse_file(pemfile)
        private_key = str(certs[0])
        client = OAuth2Session(
            client_id=client_id, client_secret=private_key, token_endpoint_auth_method="private_key_jwt"
        )
        client.register_client_auth_method(PrivateKeyJWT(token_url))
        resp = client.fetch_token(token_url, grant_type="client_credentials")

        newtoken = resp["access_token"]

        with open(rawfile, "w") as myfile:
            myfile.write(newtoken)
        return newtoken

    def get_headers2(self, access_token):
        headers = {}
        headers["content-type"] = "application/x-www-form-urlencoded"
        headers["Authorization"] = "Bearer %s" % access_token
        return headers

    def requests_nersc(self, username):
        # /etc/decisionengine/config.d/Nersc.jsonnet needs to also have
        # "query_url": "https://api.nersc.gov/api/v1.2/account/projects",
        p_url = self.constraints.get("query_url")
        my_access_token = self.check_accesstoken(username)
        my_header = self.get_headers2(my_access_token)
        r = requests.request(method="GET", url=p_url, headers=my_header)
        returndict = json.loads(r.text)
        return returndict

    def send_query(self):
        results = []
        for username in self.constraints.get("usernames", []):
            returned_list = self.requests_nersc(username)
            for each_dict in returned_list:
                # HK> This if condition will choose only m3249 for fife and discard m3990
                if each_dict["repo_name"] == self.localmap[username]:
                    local_dict = {each_key: each_dict[each_key] for each_key in self.keys_list}
                    local_dict['real_name'] = username
                    results.append(local_dict)
        return results

    def acquire(self):
        self.logger.debug("in NerscSFApi acquire")
        return {"Nersc_Allocation_SFAPI": pd.DataFrame(self.send_query())}


Source.describe(NerscSFApi)
