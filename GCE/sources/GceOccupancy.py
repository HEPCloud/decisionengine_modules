"""
Get GCE occupancies
"""
import argparse
import os
import pprint
import pandas as pd

import google.auth
import googleapiclient.discovery

# https://github.com/googleapis/google-api-python-client/issues/299#issuecomment-268915510
# check if our oauth2client supports cache_discovery or not
import oauth2client
from packaging import version

from decisionengine.framework.modules import Source
from decisionengine_modules.util.retry_function import retry_wrapper

PRODUCES = ["GCE_Occupancy"]

_MAX_RETRIES = 10
_RETRY_TIMEOUT = 10


class GceOccupancy(Source.Source):

    def __init__(self, config):
        super(GceOccupancy, self).__init__(config)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["credential"]
        credentials, self.project = google.auth.default()

        use_cache = version.parse(oauth2client.__version__) < version.parse('4.0.0')
        self.client = googleapiclient.discovery.build(
            "compute", "v1", credentials=credentials,
            cache_discovery=use_cache)
        self.max_retries = config.get("max_retries", _MAX_RETRIES)
        self.retry_timeout = config.get("retry_timeout", _RETRY_TIMEOUT)

    def produces(self, name_schema_id_list=None):
        return PRODUCES

    def _get_client(self):
        return self.client

    def acquire(self):
        return retry_wrapper(self._acquire, self.max_retries, self.retry_timeout, backoff=False)

    def _acquire(self):
        d = {}
        request = self._get_client().instances().aggregatedList(project=self.project)
        while request is not None:
            response = request.execute()
            for name, instances_scoped_list in response["items"].items():
                if "instances" in instances_scoped_list:
                    instances = instances_scoped_list.get("instances", [])
                    for instance in instances:
                        instance_type = instance.get(
                            "machineType").split("/").pop()
                        zone = instance.get("zone").split("/").pop()
                        status = instance.get("status")
                        key = "{}:{}".format(instance_type,
                                             zone)
                        if status == "RUNNING":
                            # TODO: Order matters for the test, need to REVISIT.
                            data = d.setdefault(key, {"AvailabilityZone": zone,
                                                      "InstanceType": instance_type,
                                                      "Occupancy": 0})
                            data["Occupancy"] += 1

            request = self._get_client().instances().aggregatedList_next(previous_request=request,
                                                                         previous_response=response)
        df = pd.DataFrame(d.values())
        return {PRODUCES[0]: df}


def module_config_template():
    """
    Print template for this module configuration
    """
    template = {
        'gce_occupancy': {
            'module': 'decisionengine_modules.GCE.sources.GceOccupancy',
            'name': 'GceOccupancy',
            'parameters': {
                'credential': '/etc/gwms-frontend/credentials/monitoring.json',
                'max_retries': 10,
                'retry_timeout': 10,
            }
        }
    }
    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print('produces %s' % PRODUCES)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configtemplate',
        action='store_true',
        help='prints the expected module configuration')

    parser.add_argument(
        '--configinfo',
        action='store_true',
        help='prints config template along with produces and consumes info')
    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == '__main__':
    main()
