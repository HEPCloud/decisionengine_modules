import numpy as np
import pandas as pd

class HTCondorJobQ(Source):
    PRODUCES = ["job_manifests"]

    def __init__ (self, *args, **kwargs):
        self.desired_attrs = kwargs["desired_attrs"]
        self.constraint = kwargs["constraint"]
        self.schedd_name = kwargs["schedd_name"]

    def produces(self): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        job_manifests = [
            {"ProcId": 1, "ClusterId": 0, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 2, "ClusterId": 0, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 3, "ClusterId": 0, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 3, "ClusterId": 1, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 3, "ClusterId": 2, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 6, "ClusterId": 0, "CPUS": 2, "MEM": 4, "MEM_UNITS": "MB",}
        ]
        manifest_keys = job_manifests[0].keys()
        pandas_data = {}
        for key in manifest_keys:
            pandas_data[key] = pd.Series([d[key] for d in job_manifests])
        DataBlock["job_manifests"] = pandas_data
