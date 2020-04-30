import os

import numpy as np
import pandas as pd

from decisionengine_modules.GCE.transforms import GceBurnRate

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "GceOccupancy.output.fixture.csv")
OCCUPANCY = pd.read_csv(CSV_FILE)

PRODUCES = ["GCE_Burn_Rate"]
CONFIG = {
}


performance = pd.DataFrame([
    {"EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
     "InstanceType": "n1-standard-1",
     "AvailabilityZone": "us-central1-a",
     "OnDemandPrice": 0.0475,
     "PreemptiblePrice": 0.01,
     "PerfTtbarTotal": 0.0317}])


"""
expected datablock
"""
data_block = {
    "GCE_Instance_Performance": performance.reindex(columns=("EntryName",
                                                             "InstanceType",
                                                             "AvailabilityZone",
                                                             "OnDemandPrice",
                                                             "PreemptiblePrice",
                                                             "PerfTtbarTotal")),
    "GCE_Occupancy": OCCUPANCY,
}

expected_transform_output = {
    PRODUCES[0]: pd.DataFrame([{
        "BurnRate": 0.1}])
}


class TestGceBurnRate:

    def test_produces(self):
        gce_burn_rate = GceBurnRate.GceBurnRate(CONFIG)
        assert gce_burn_rate.produces() == PRODUCES

    def test_transform(self):
        gce_burn_rate = GceBurnRate.GceBurnRate(CONFIG)
        res = gce_burn_rate.transform(data_block)
        assert PRODUCES.sort() == list(res.keys()).sort()

        expected_df = expected_transform_output[PRODUCES[0]]
        res_df = res[PRODUCES[0]]
        assert np.isclose(expected_df["BurnRate"],
                          res_df["BurnRate"])
