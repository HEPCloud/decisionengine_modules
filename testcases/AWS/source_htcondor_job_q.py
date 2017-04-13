import numpy as np
import pandas as pd

class HTCondorJobQ(Source):
    PRODUCES = ["job_manifests"]

<<<<<<< HEAD
    def __init__ (self, params_dict):
        self.desired_attrs = params_dict["desired_attrs"]
        self.constraint = params_dict["constraint"]
        self.schedd_name = params_dict["schedd_name"]
=======
    def __init__ (self, *args, **kwargs):
        self.desired_attrs = kwargs["desired_attrs"]
        self.constraint = kwargs["constraint"]
        self.schedd_name = kwargs["schedd_name"]
>>>>>>> new source for provisioner, changed htcondor q to convert data to pandas style data

    def produces(self): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        job_manifests = [
<<<<<<< HEAD
            {"JobId": "1.0", "JOB_CPUS": 2, "JOB_MEM": 4, "JOB_MEM_UNITS": "GB"},
            {"JobId": "2.0", "JOB_CPUS": 2, "JOB_MEM": 4, "JOB_MEM_UNITS": "GB"},
            {"JobId": "3.0", "JOB_CPUS": 2, "JOB_MEM": 4, "JOB_MEM_UNITS": "GB"},
            {"JobId": "3.1", "JOB_CPUS": 2, "JOB_MEM": 4, "JOB_MEM_UNITS": "GB"},
            {"JobId": "3.2", "JOB_CPUS": 2, "JOB_MEM": 4, "JOB_MEM_UNITS": "GB"},
            {"JobId": "6.0", "JOB_CPUS": 2, "JOB_MEM": 4, "JOB_MEM_UNITS": "GB"}
=======
            {"ProcId": 1, "ClusterId": 0, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 2, "ClusterId": 0, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 3, "ClusterId": 0, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 3, "ClusterId": 1, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 3, "ClusterId": 2, "CPUS": 2, "MEM": 4, "MEM_UNITS": "GB",},
            {"ProcId": 6, "ClusterId": 0, "CPUS": 2, "MEM": 4, "MEM_UNITS": "MB",}
>>>>>>> new source for provisioner, changed htcondor q to convert data to pandas style data
        ]
        manifest_keys = job_manifests[0].keys()
        pandas_data = {}
        for key in manifest_keys:
            pandas_data[key] = pd.Series([d[key] for d in job_manifests])
<<<<<<< HEAD
        DataBlock["job_manifests"] = pd.DataFrame(pandas_data)
=======
        DataBlock["job_manifests"] = pandas_data
>>>>>>> new source for provisioner, changed htcondor q to convert data to pandas style data
