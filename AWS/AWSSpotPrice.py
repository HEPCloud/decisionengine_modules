import numpy as np
import pandas as pd

from decisionengine.framework.modules import Source

PRODUCES = ["provisioner_resource_spot_prices"]
class AWSSpotPrice(Source.Source):

    def __init__ (self, *args, **kwargs):
        pass

    def produces(self,schema_id_list): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self):
        resource_list = [
            {"ResourceName": "AWS1", "SpotPrice": 1.},
            {"ResourceName": "AWS2", "SpotPrice": 2.},
            {"ResourceName": "AWS3", "SpotPrice": 2.},
            {"ResourceName": "AWS4", "SpotPrice": 1.},
            {"ResourceName": "AWS5", "SpotPrice": 2.}
        ]

        resource_keys = resource_list[0].keys()
        pandas_data = {}
        for key in resource_keys:
            pandas_data[key] = pd.Series([d[key] for d in resource_list])

        return {"provisioner_resource_spot_prices": pd.DataFrame(pandas_data)}

if __name__ == "__main__":
    sp = AWSSpotPrice()
    rc = sp.acquire()
    print(rc)
