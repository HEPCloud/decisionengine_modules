import pandas as pd

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
    "Gce_Instance_Performance" : gce_instance_performance_df.reindex(columns = ("EntryName",
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
     "PricePerformance" : 0.67 },])

expected_transform_output = {
    produces[0] : gce_price_performance_df.reindex(columns = ("EntryName",
                                              "PricePerformance")),
    produces[1] : pd.DataFrame([
        {"EntryName" : "CMSHTPC_T3_US_GCE_Cori",
         "FigureOfMerit" : 0.33
        },]),
}


class TestGceFigureOfMerit:

    def test_produces(self):
        gce_figure_of_merit = GceFigureOfMerit.GceFigureOfMerit(config)
        assert gce_figure_of_merit.produces() == produces

    def test_transform(self):
        gce_figure_of_merit = GceFigureOfMerit.GceFigureOfMerit(config)
        res = gce_figure_of_merit.transform(data_block)
        assert produces == res.keys()
        for key, value in res.items():
            try:
                assert expected_transform_output[key].equals(value)
            except:
                print key, " fail\n", expected_transform_output[key], "\n", value

