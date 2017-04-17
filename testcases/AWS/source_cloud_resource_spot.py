import numpy as np
import pandas as pd

class ProvisionerResourceList(Source):
    PRODUCES = ["provisioner_resource_spot_prices"]

    def __init__ (self, *args, **kwargs):
        pass

    def produces(self): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        resource_list = [
            {"RESOURCE_NAME": "AWS1", "SPOT": 1},
            {"RESOURCE_NAME": "AWS2", "SPOT": 2},
            {"RESOURCE_NAME": "AWS3", "SPOT": 2},
            {"RESOURCE_NAME": "AWS4", "SPOT": 1},
            {"RESOURCE_NAME": "AWS5", "SPOT": 2}
        ]
        resource_keys = resource_list[0].keys()
        pandas_data = {}
        for key in resource_keys:
            pandas_data[key] = pd.Series([d[key] for d in resource_list])
        DataBlock["provisioner_resource_spot_prices"] = pd.DataFrame(pandas_data)
