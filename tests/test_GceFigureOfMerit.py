import math 
import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np

from decisionengine_modules.GCE.transforms import GceFigureOfMerit

produces = ["GCE_Price_Performance", "GCE_Figure_Of_Merit"]

config = {
}

gce_instance_performance_df =  pd.DataFrame([
        {"EntryName" : "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
         "InstanceType" : "n1-standard-1",
         "AvailabilityZone" : "us-central1-a" ,
         "OnDemandPrice" : 0.0475,
         "PerfTtbarTotal" : 0.0317 },])

gce_instance_performance_df.reindex(columns = ("EnryName",
                                                "InstanceType",
                                                "AvailabilityZone",
                                                "OnDemandPrice",
                                                "PerfTtbarTotal"))

data_block = {
    "GCE_Instance_Performance" : gce_instance_performance_df.reindex(columns = ("EntryName",
                                                 "InstanceType",
                                                 "AvailabilityZone",
                                                 "OnDemandPrice",
                                                 "PerfTtbarTotal")),
    "Factory_Entries_LCF" : pd.DataFrame([
        {"EntryName" : "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
         "GlideinConfigPerEntryMaxGlideins" : 200,
         "GlideinMonitorTotalStatusRunning" : 100},]),
}

gce_price_performance_df = pd.DataFrame([
    {"EntryName" : "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
     "PricePerformance" : 1.498423 },])

expected_transform_output = {
    produces[0] : gce_price_performance_df.reindex(columns = ("EntryName",
                                              "PricePerformance")),
    produces[1] : pd.DataFrame([
        {"EntryName" : "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
         "FigureOfMerit" : 0.749211
        },]),
}


class TestGceFigureOfMerit:

    def test_produces(self):
        gce_figure_of_merit = GceFigureOfMerit.GceFigureOfMerit(config)
        assert gce_figure_of_merit.produces() == produces

    def test_transform(self):
        gce_figure_of_merit = GceFigureOfMerit.GceFigureOfMerit(config)
        res = gce_figure_of_merit.transform(data_block)
        assert produces.sort() == res.keys().sort()
        
        expected_df  =  expected_transform_output[produces[0]]
        expected_fom  = expected_df['FigureOfMerit']

        res_df = res[produces[0]]
        res_fom = res_df['FigureOfMerit']
        
        assert  np.isclose(expected_fom, res_fom)
        
        expected_df  =  expected_transform_output[produces[1]]
        expected_pp  = expected_df['PricePerformance']

        res_df = res[produces[1]]
        res_pp = res_df['PricePerformance']
        
        assert  np.isclose(expected_pp, res_pp)
