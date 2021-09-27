"""
Get GCE occupancies
"""
import os

import google.auth
import googleapiclient.discovery

# https://github.com/googleapis/google-api-python-client/issues/299#issuecomment-268915510
# check if our oauth2client supports cache_discovery or not
import oauth2client
import pandas as pd

from packaging import version

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.util.retry_function import retry_wrapper

_MAX_RETRIES = 10
_RETRY_TIMEOUT = 10


@Source.supports_config(
    Parameter("credential", type=str, comment="file that stores credentials in JSON"),
    Parameter("max_retries", default=_MAX_RETRIES),
    Parameter("retry_timeout", default=_RETRY_TIMEOUT),
)
@Source.produces(GCE_Occupancy=pd.DataFrame)
class GceOccupancy(Source.Source):
    def __init__(self, config):
        super().__init__(config)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["credential"]
        credentials, self.project = google.auth.default()

        use_cache = version.parse(oauth2client.__version__) < version.parse("4.0.0")
        self.client = googleapiclient.discovery.build(
            "compute", "v1", credentials=credentials, cache_discovery=use_cache
        )
        self.max_retries = config.get("max_retries", _MAX_RETRIES)
        self.retry_timeout = config.get("retry_timeout", _RETRY_TIMEOUT)

    def _get_client(self):
        return self.client

    def acquire(self):
        self.logger.debug("in GCEOccupancy acquire")
        return retry_wrapper(self._acquire, self.max_retries, self.retry_timeout, backoff=False, logger=self.logger)

    def _acquire(self):
        d = {}
        request = self._get_client().instances().aggregatedList(project=self.project)
        while request is not None:
            response = request.execute()
            for _name, instances_scoped_list in response["items"].items():
                if "instances" in instances_scoped_list:
                    instances = instances_scoped_list.get("instances", [])
                    for instance in instances:
                        instance_type = instance.get("machineType").split("/").pop()
                        zone = instance.get("zone").split("/").pop()
                        status = instance.get("status")
                        key = f"{instance_type}:{zone}"
                        if status == "RUNNING":
                            # TODO: Order matters for the test, need to REVISIT.
                            data = d.setdefault(
                                key, {"AvailabilityZone": zone, "InstanceType": instance_type, "Occupancy": 0}
                            )
                            data["Occupancy"] += 1

            request = (
                self._get_client().instances().aggregatedList_next(previous_request=request, previous_response=response)
            )
        df = pd.DataFrame(d.values())
        return {"GCE_Occupancy": df}


Source.describe(GceOccupancy)
