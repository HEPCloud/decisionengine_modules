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
            {"ResourceName": "AWS1", "SpotPrice": 1},
            {"ResourceName": "AWS2", "SpotPrice": 2},
            {"ResourceName": "AWS3", "SpotPrice": 2},
            {"ResourceName": "AWS4", "SpotPrice": 1},
            {"ResourceName": "AWS5", "SpotPrice": 2}
        ]

        resource_keys = resource_list[0].keys()
        pandas_data = {}
        for key in resource_keys:
            pandas_data[key] = pd.Series([d[key] for d in resource_list])

        return { "provisioner_resource_spot_prices": pd.DataFrame(pandas_data) }
