import numpy as np
import pandas as pd

from decisionengine.framework.modules import Transform

CONSUMES = ["job_manifests", "provisioner_resources",
            "provisioner_resource_spot_prices"]
PRODUCES = ["jobs", "resource_requests"]


class CloudRequests(Transform.Transform):

    def __init__(self, param_dict):
        pass

    # name_list:  A list of the data product names that the Transform will consume
    def consumes(self):
        return CONSUMES

    def produces(self, schema_id_list):
        return PRODUCES

    def _load_data_frame(self, list_of_dicts):
        list_of_keys = list_of_dicts[0].keys()
        pandas_data = {}
        print("CloudRequest list of keys", list_of_keys)
        for key in list_of_keys:
            pandas_data[key] = pd.Series([d[key] for d in list_of_dicts])
        return pd.DataFrame(pandas_data)

    def transform(self, DataBlock):
        job_manifests_pd = DataBlock["job_manifests"]
        resources_pd = DataBlock["provisioner_resources"]
        spot_pd = DataBlock["provisioner_resource_spot_prices"]

        # If this were a real transform, we'd do a lot of data manipulation here
        # instead, because Tony is still learning Pandas and ran out of time for
        # the code sprint, we are just going to push out dummy data

        job_manifests = [
            {"JobId": "1.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS1", "ResourceCpus": 2,
                "ResourceMemory": 8, "EC2Type": "m4.large", "SpotPrice": .1, "estimated_cost": 1.2, "burn_rate": .1},
            {"JobId": "1.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS2", "ResourceCpus": 4,
                "ResourceMemory": 16, "EC2Type": "m4.xlarge", "SpotPrice": .15, "estimated_cost": 1.8, "burn_rate": .15},
            {"JobId": "1.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS3", "ResourceCpus": 2,
                "ResourceMemory": 7.5, "EC2Type": "m3.large", "SpotPrice": .2, "estimated_cost": 2.4, "burn_rate": .2},
            {"JobId": "1.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS4", "ResourceCpus": 4,
                "ResourceMemory": 15, "EC2Type": "m3.xlarge", "SpotPrice": .12, "estimated_cost": 1.44, "burn_rate": .12},
            {"JobId": "1.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS5", "ResourceCpus": 4,
                "ResourceMemory": 7.5, "EC2Type": "c4.xlarge", "SpotPrice": .14, "estimated_cost": 1.68, "burn_rate": .14},
            {"JobId": "2.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS1", "ResourceCpus": 2,
                "ResourceMemory": 8, "EC2Type": "m4.large", "SpotPrice": .1, "estimated_cost": 1.2, "burn_rate": .1},
            {"JobId": "2.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS2", "ResourceCpus": 4,
                "ResourceMemory": 16, "EC2Type": "m4.xlarge", "SpotPrice": .15, "estimated_cost": 1.8, "burn_rate": .15},
            {"JobId": "2.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS3", "ResourceCpus": 2,
                "ResourceMemory": 7.5, "EC2Type": "m3.large", "SpotPrice": .2, "estimated_cost": 2.4, "burn_rate": .2},
            {"JobId": "2.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS4", "ResourceCpus": 4,
                "ResourceMemory": 15, "EC2Type": "m3.xlarge", "SpotPrice": .12, "estimated_cost": 1.44, "burn_rate": .12},
            {"JobId": "2.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS5", "ResourceCpus": 4,
                "ResourceMemory": 7.5, "EC2Type": "c4.xlarge", "SpotPrice": .14, "estimated_cost": 1.68, "burn_rate": .14},
            {"JobId": "3.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS1", "ResourceCpus": 2,
                "ResourceMemory": 8, "EC2Type": "m4.large", "SpotPrice": .1, "estimated_cost": 1.2, "burn_rate": .1},
            {"JobId": "3.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS2", "ResourceCpus": 4,
                "ResourceMemory": 16, "EC2Type": "m4.xlarge", "SpotPrice": .15, "estimated_cost": 1.8, "burn_rate": .15},
            {"JobId": "3.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS3", "ResourceCpus": 2,
                "ResourceMemory": 7.5, "EC2Type": "m3.large", "SpotPrice": .2, "estimated_cost": 2.4, "burn_rate": .2},
            {"JobId": "3.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS4", "ResourceCpus": 4,
                "ResourceMemory": 15, "EC2Type": "m3.xlarge", "SpotPrice": .12, "estimated_cost": 1.44, "burn_rate": .12},
            {"JobId": "3.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS5", "ResourceCpus": 4,
                "ResourceMemory": 7.5, "EC2Type": "c4.xlarge", "SpotPrice": .14, "estimated_cost": 1.68, "burn_rate": .14},
            {"JobId": "3.1", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS1", "ResourceCpus": 2,
                "ResourceMemory": 8, "EC2Type": "m4.large", "SpotPrice": .1, "estimated_cost": 1.2, "burn_rate": .1},
            {"JobId": "3.1", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS2", "ResourceCpus": 4,
                "ResourceMemory": 16, "EC2Type": "m4.xlarge", "SpotPrice": .15, "estimated_cost": 1.8, "burn_rate": .15},
            {"JobId": "3.1", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS3", "ResourceCpus": 2,
                "ResourceMemory": 7.5, "EC2Type": "m3.large", "SpotPrice": .2, "estimated_cost": 2.4, "burn_rate": .2},
            {"JobId": "3.1", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS4", "ResourceCpus": 4,
                "ResourceMemory": 15, "EC2Type": "m3.xlarge", "SpotPrice": .12, "estimated_cost": 1.44, "burn_rate": .12},
            {"JobId": "3.1", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS5", "ResourceCpus": 4,
                "ResourceMemory": 7.5, "EC2Type": "c4.xlarge", "SpotPrice": .14, "estimated_cost": 1.68, "burn_rate": .14},
            {"JobId": "3.2", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS1", "ResourceCpus": 2,
                "ResourceMemory": 8, "EC2Type": "m4.large", "SpotPrice": .1, "estimated_cost": 1.2, "burn_rate": .1},
            {"JobId": "3.2", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS2", "ResourceCpus": 4,
                "ResourceMemory": 16, "EC2Type": "m4.xlarge", "SpotPrice": .15, "estimated_cost": 1.8, "burn_rate": .15},
            {"JobId": "3.2", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS3", "ResourceCpus": 2,
                "ResourceMemory": 7.5, "EC2Type": "m3.large", "SpotPrice": .2, "estimated_cost": 2.4, "burn_rate": .2},
            {"JobId": "3.2", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS4", "ResourceCpus": 4,
                "ResourceMemory": 15, "EC2Type": "m3.xlarge", "SpotPrice": .12, "estimated_cost": 1.44, "burn_rate": .12},
            {"JobId": "3.2", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS5", "ResourceCpus": 4,
                "ResourceMemory": 7.5, "EC2Type": "c4.xlarge", "SpotPrice": .14, "estimated_cost": 1.68, "burn_rate": .14},
            {"JobId": "6.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS1", "ResourceCpus": 2,
                "ResourceMemory": 8, "EC2Type": "m4.large", "SpotPrice": .1, "estimated_cost": 1.2, "burn_rate": .1},
            {"JobId": "6.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS2", "ResourceCpus": 4,
                "ResourceMemory": 16, "EC2Type": "m4.xlarge", "SpotPrice": .15, "estimated_cost": 1.8, "burn_rate": .15},
            {"JobId": "6.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS3", "ResourceCpus": 2,
                "ResourceMemory": 7.5, "EC2Type": "m3.large", "SpotPrice": .2, "estimated_cost": 2.4, "burn_rate": .2},
            {"JobId": "6.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS4", "ResourceCpus": 4,
                "ResourceMemory": 15, "EC2Type": "m3.xlarge", "SpotPrice": .12, "estimated_cost": 1.44, "burn_rate": .12},
            {"JobId": "6.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12, "ResourceName": "AWS5", "ResourceCpus": 4,
                "ResourceMemory": 7.5, "EC2Type": "c4.xlarge", "SpotPrice": .14, "estimated_cost": 1.68, "burn_rate": .14}
        ]

        jobs_pd = self._load_data_frame(job_manifests)
        requests = [{"ResourceName": "AWS1", "Count": 6}, ]

        return {"jobs": jobs_pd, "resource_requests": requests}
