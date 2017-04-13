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
            {"NAME": "AWS1", "CPUS": 1, "MEMORY": 2, "MEMORY_UNITS": "GB"},
            {"NAME": "AWS2", "CPUS": 2, "MEMORY": 4, "MEMORY_UNITS": "GB"},
            {"NAME": "AWS3", "CPUS": 2, "MEMORY": 6, "MEMORY_UNITS": "GB"},
            {"NAME": "AWS4", "CPUS": 1, "MEMORY": 6, "MEMORY_UNITS": "GB"},
            {"NAME": "AWS5", "CPUS": 2, "MEMORY": 5, "MEMORY_UNITS": "GB"}
        ]
        resource_keys = resource_list[0].keys()
        pandas_data = {}
        for key in resource_keys:
            pandas_data[key] = pd.Series([d[key] for d in resource_list])
        DataBlock["provisioner_resources"] = pandas_data
