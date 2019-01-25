import math
import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np
from decisionengine_modules.GCE.transforms import GceBurnRate

produces = ["GCE_Burn_Rate"]

config = {
}

occupancy = pd.read_csv("GceOccupancy.output.fixture.csv")

performance =  pd.DataFrame([
    {"EntryName" : "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
     "InstanceType" : "n1-standard-1",
     "AvailabilityZone" : "us-central1-a" ,
     "OnDemandPrice" : 0.0475,
     "PreemptiblePrice" : 0.01, 
     "PerfTtbarTotal" : 0.0317 },])


"""
expected datablock
"""
data_block = {
    "GCE_Instance_Performance" : performance.reindex(columns = ("EntryName",
                                                                "InstanceType",
                                                                "AvailabilityZone",
                                                                "OnDemandPrice",
                                                                "PreemptiblePrice",
                                                                "PerfTtbarTotal")),
    "GCE_Occupancy" : occupancy,
}

expected_transform_output = {
    produces[0] : pd.DataFrame([{
        "BurnRate" : 0.1}])
}                           

class TestGceBurnRate:

    def test_produces(self):
        gce_burn_rate = GceBurnRate.GceBurnRate(config)
        assert gce_burn_rate.produces() == produces

    def test_transform(self):
        gce_burn_rate = GceBurnRate.GceBurnRate(config)
        res = gce_burn_rate.transform(data_block)
        assert produces.sort() == res.keys().sort()

        expected_df = expected_transform_output[produces[0]]
        res_df = res[produces[0]]
        assert  np.isclose(expected_df["BurnRate"],
                           res_df["BurnRate"])
