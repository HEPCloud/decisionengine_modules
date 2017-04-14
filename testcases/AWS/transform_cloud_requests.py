import numpy as np
import pandas as pd

class CloudRequests(Transform):
    CONSUMES = ["job_manifests", "provisioner_resources"]
    PRODUCES = []

    def __init__(self, para_dict):
      pass

    # name_list:  A list of the data product names that the Transform will consume
    def consumes():
        return CONSUMES

    def produces():
        return PRODUCES

    def transform(DataBlock):
        Jobs = DataBlock["job_manifests"]
        resources = DataBlock["provisioner_resources"]
        
