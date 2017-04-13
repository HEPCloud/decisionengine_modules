import numpy as np
import pandas as pd

class HTCondorJobQ(Source):
    PRODUCES = ["job_manifests"]

    def __init__ (self, params_dict):
        self.desired_attrs = params_dict["desired_attrs"]
        self.constraint = params_dict["constraint"]
        self.schedd_name = params_dict["schedd_name"]

    def produces(self): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        job_manifests = [
            {"JobId": "1.0", "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"JobId": "2.0", "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"JobId": "3.0", "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"JobId": "3.1", "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"JobId": "3.2", "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"JobId": "6.0", "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",}
        ]
        manifest_keys = job_manifests[0].keys()
        pandas_data = {}
        for key in manifest_keys:
            pandas_data[key] = pd.Series([d[key] for d in job_manifests])
        DataBlock["job_manifests"] = pandas_data
