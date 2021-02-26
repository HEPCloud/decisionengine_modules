import pandas as pd

from decisionengine.framework.modules import Source

class HTCondorJobQ(Source):
    PRODUCES = ["job_manifests"]

    def __init__(self, params_dict):
        self.desired_attrs = params_dict["desired_attrs"]
        self.constraint = params_dict["constraint"]
        self.schedd_name = params_dict["schedd_name"]

    def produces(self):
        return self.PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        # JobId == ClusterId.ProcId
        job_manifests = [
            {"JobId": "1.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "2.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "3.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "3.1", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "3.2", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "6.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12}
        ]
        manifest_keys = job_manifests[0].keys()
        pandas_data = {}
        for key in manifest_keys:
            pandas_data[key] = pd.Series([d[key] for d in job_manifests])

        return {"job_manifests": pd.DataFrame(pandas_data)}
