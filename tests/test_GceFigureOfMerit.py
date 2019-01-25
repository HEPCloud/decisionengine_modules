import pandas as pd
import numpy as np
from decisionengine_modules.GCE.transforms import GceFigureOfMerit
import tabulate 


produces = ["GCE_Price_Performance", "GCE_Figure_Of_Merit"]

config = {
}

"""
GCE occupancy DF
"""
gce_occupancy_df = pd.read_csv("GceOccupancy.output.fixture.csv")

"""
GCE Instance Performance DF
"""
gce_instance_performance_df =  pd.DataFrame([
        {"EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
         "InstanceType": "n1-standard-1",
         "AvailabilityZone": "us-central1-a",
         "OnDemandPrice": 0.0475,
         "PerfTtbarTotal": 0.0317}, ])

gce_instance_performance_df.reindex(columns=("EnryName",
                                             "InstanceType",
                                             "AvailabilityZone",
                                             "OnDemandPrice",
                                             "PerfTtbarTotal"))

"""
expected datablock
"""
data_block = {
    "GCE_Instance_Performance": gce_instance_performance_df.reindex(columns=("EntryName",
                                                 "InstanceType",
                                                 "AvailabilityZone",
                                                 "OnDemandPrice",
                                                 "PerfTtbarTotal")),
    "Factory_Entries_GCE": pd.DataFrame([
        {"EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
         "GlideinConfigPerEntryMaxIdle": 100,
         "GlideinMonitorTotalStatusIdle": 10,
         "GlideinConfigPerEntryMaxGlideins": 200,
         "GlideinMonitorTotalStatusRunning": 100},]),

    "GCE_Occupancy": gce_occupancy_df,
}

gce_price_performance_df = pd.DataFrame([
    {"EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
     "PricePerformance": 1.498423}, ])

expected_transform_output = {
    produces[0]: gce_price_performance_df.reindex(columns=("EntryName",
                                                           "PricePerformance")),
    produces[1]: pd.DataFrame([
        {"EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
         "FigureOfMerit": 0.08241324921135648
        }, ]),
}

for k, value in data_block.items():
    print tabulate.tabulate(value, headers='keys', tablefmt='psql')


class TestGceFigureOfMerit:

    def test_produces(self):
        gce_figure_of_merit = GceFigureOfMerit.GceFigureOfMerit(config)
        assert gce_figure_of_merit.produces() == produces

    def test_transform(self):
        gce_figure_of_merit = GceFigureOfMerit.GceFigureOfMerit(config)
        res = gce_figure_of_merit.transform(data_block)
        assert produces.sort() == res.keys().sort()

        expected_df = expected_transform_output[produces[0]]
        res_df = res[produces[0]]
        assert np.isclose(expected_df["FigureOfMerit"],
                          res_df["FigureOfMerit"])

        expected_df = expected_transform_output[produces[1]]
        res_df = res[produces[1]]
        assert np.isclose(expected_df["PricePerformance"],
                          res_df["PricePerformance"])


