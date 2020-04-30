import numpy as np
import pandas as pd

from decisionengine.framework.modules import Source

PRODUCES = ["provisioner_resources"]


class ProvisionerResourceList(Source.Source):

    def __init__(self, *args, **kwargs):
        pass

    def produces(self, schema_id_list):
        return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self):
        resource_list = [
            {"ResourceName": "AWS1", "ResourceCpus": 2,
                "ResourceMemory": 8, "EC2Type": "m4.large"},
            {"ResourceName": "AWS2", "ResourceCpus": 4,
                "ResourceMemory": 16, "EC2Type": "m4.xlarge"},
            {"ResourceName": "AWS3", "ResourceCpus": 2,
                "ResourceMemory": 7.5, "EC2Type": "m3.large"},
            {"ResourceName": "AWS4", "ResourceCpus": 4,
                "ResourceMemory": 15, "EC2Type": "m3.xlarge"},
            {"ResourceName": "AWS5", "ResourceCpus": 4,
                "ResourceMemory": 7.5, "EC2Type": "c4.xlarge"}
        ]
        resource_keys = resource_list[0].keys()
        pandas_data = {}
        for key in resource_keys:
            pandas_data[key] = pd.Series([d[key] for d in resource_list])

        return {"provisioner_resources": pd.DataFrame(pandas_data)}
