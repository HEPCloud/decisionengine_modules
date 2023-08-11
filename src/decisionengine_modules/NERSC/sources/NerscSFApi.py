import pandas as pd
from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.NERSC.util import newt
from datetime import datetime
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc7523               import PrivateKeyJWT
import pem
import jwt
import requests
import json
import time, os

@Source.supports_config(Parameter('constraints', type=dict, comment="""Supports the layout:"""))
@Source.produces(Nersc_Allocation_SFAPI=pd.DataFrame)
class NerscSFApi(Source.Source):

    def __init__(self, config):
        super().__init__(config)

        self.constraints = config.get('constraints')
        if not isinstance(self.constraints, dict):
            raise RuntimeError('constraints should be a dict')

        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )
        self.localmap = {'uscms': 'm2612', 'fife': 'm3249'}
        self.keys_list = [ 'hours_given','hours_used','id', 'project_hours_given', 'project_hours_used', 'repo_name' ]

    def check_accesstoken(self, nersc_user ):
        token_url = "https://oidc.nersc.gov/c2id/token"
        currenttime = time.time()
        renew_bool = False

        rawfile_ucms = '/tmp/ucms_access.token'
        rawfile_fife = '/tmp/fife_access.token'

# These 4 variables are defined in /etc/decisionengine/config.d/Nersc.jsonnet
#          "ucms_private_key": "/etc/decisionengine/modules.data/ucms_privkey.pem",
#          "fife_private_key": "/etc/decisionengine/modules.data/fife_privkey.pem",
#          "ucms_client_id":   "/etc/decisionengine/modules.data/ucms_clientid.txt",
#          "fife_client_id":   "/etc/decisionengine/modules.data/fife_clientid.txt"
# And the actual key files and id files reside in /etc/decisionengine/modules.data/
# So, puppet should copy these 4 files from 
# ssiadmin4:/srv/secrets/per_host/hepcsvc03.fnal.gov/credentials/
        pemfile_ucms   = self.constraints.get('ucms_private_key')
        pemfile_fife   = self.constraints.get('fife_private_key')
        client_id_ucms = self.constraints.get('ucms_client_id')
        client_id_fife = self.constraints.get('fife_client_id')

        rawfile = None
        pemfile = None
        client_id = None
        if nersc_user == 'uscms':
            rawfile   = rawfile_ucms
            pemfile   = pemfile_ucms
            with open( client_id_ucms, 'r' ) as ifile:
                client_id =  ifile.read( )
                client_id = client_id.rstrip()
        elif nersc_user == 'fife':
            rawfile   = rawfile_fife
            pemfile   = pemfile_fife
            with open( client_id_fife, 'r' ) as ifile:
                client_id = ifile.read( )
                client_id = client_id.rstrip()
        else:
            self.logger.error("Unknown user, exiting" )
            return None

        if not os.path.exists( rawfile ):
            self.logger.debug(f"{rawfile} does not exist. Need to generate")
            renew_bool = True
        else:
            atoken = None
            with open( rawfile, 'r' ) as afile:
                atoken = afile.read( )
                atoken = atoken.rstrip()
#HK> If the access token is expired, the flow goes directly to except jwt.ExpiredSignatureError
            try:
                result = jwt.decode(atoken, options={"verify_signature": False})
                self.logger.debug("Not expired. Returning without generating a new access token" )
                return atoken # This means the existing access token is not expired.

            except jwt.ExpiredSignatureError:
                self.logger.debug("Access Token expired" )
                renew_bool = True

        if renew_bool:
            certs = pem.parse_file( pemfile )
            private_key = str( certs[0] )
            client = OAuth2Session(client_id=client_id,client_secret=private_key,token_endpoint_auth_method="private_key_jwt")
            client.register_client_auth_method(  PrivateKeyJWT( token_url )  )
            resp = client.fetch_token( token_url, grant_type="client_credentials" )

            newtoken = resp[ "access_token" ]

            with open( rawfile, 'w' ) as myfile:
                myfile.write( newtoken)
            return newtoken

    def get_headers2(self, access_token ):
        headers = {}
        headers['content-type'] = 'application/x-www-form-urlencoded'
        headers['Authorization'] = 'Bearer %s'%access_token
        return headers

    def requests_nersc(self, username ):
        my_access_token = self.check_accesstoken( username )
        my_header = self.get_headers2( my_access_token )
        p_url = 'https://api.nersc.gov/api/v1.2/account/projects'
        r = requests.request(method = 'GET', url=p_url, headers=my_header)
        returndict = json.loads(r.text)
        return returndict

    def send_query(self):
        results = []
        for username in self.constraints.get("usernames", []):
            returned_list = self.requests_nersc( username )
            for each_dict in returned_list:
                #HK> This if condition will choose only m3249 for fife and discard m3990
                if each_dict['repo_name'] == self.localmap[ username ]:
                    local_dict = { each_key: each_dict[ each_key ] for each_key in self.keys_list }
                    results.append( local_dict )
        return results

    def acquire(self):
        self.logger.debug("in NerscSFApi acquire")
        return {'Nersc_Allocation_SFAPI': pd.DataFrame(self.send_query())}


Source.describe(NerscSFApi)
