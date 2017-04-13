import numpy as np
import pandas as pd

class ProvisionerResourceList(Source):
    PRODUCES = ["provisioner_resources"]

    def __init__ (self, *args, **kwargs):
        pass

    def produces(self): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        resource_list = [
            {"RESOURCE_NAME": "AWS1", "RES_CPUS": 1, "RES_MEM": 2, "RES_MEM_UNITS": "GB"},
            {"RESOURCE_NAME": "AWS2", "RES_CPUS": 2, "RES_MEM": 4, "RES_MEM_UNITS": "GB"},
            {"RESOURCE_NAME": "AWS3", "RES_CPUS": 2, "RES_MEM": 6, "RES_MEM_UNITS": "GB"},
            {"RESOURCE_NAME": "AWS4", "RES_CPUS": 1, "RES_MEM": 6, "RES_MEM_UNITS": "GB"},
            {"RESOURCE_NAME": "AWS5", "RES_CPUS": 2, "RES_MEM": 5, "RES_MEM_UNITS": "GB"}
        ]
        resource_keys = resource_list[0].keys()
        pandas_data = {}
        for key in resource_keys:
            pandas_data[key] = pd.Series([d[key] for d in resource_list])
        DataBlock["provisioner_resources"] = pd.DataFrame(pandas_data)
