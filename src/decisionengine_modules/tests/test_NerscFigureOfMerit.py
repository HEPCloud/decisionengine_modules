import pandas as pd

from decisionengine_modules.NERSC.transforms import NerscFigureOfMerit
from decisionengine.framework.modules.Module import verify_products

_produces = ['Nersc_Price_Performance', 'Nersc_Figure_Of_Merit']
produces = dict.fromkeys(_produces, pd.DataFrame)

config = {
}

nersc_instance_performance_df = pd.DataFrame([
    {"EntryName": "CMSHTPC_T3_US_NERSC_Cori",
     "InstanceType": "haswell",
     "AvailabilityZone": "cori",
     "OnDemandPrice": 0.576,
     "PerfTtbarTotal": 0.96}])

nersc_instance_performance_df.reindex(columns=("EnryName",
                                               "InstanceType",
                                               "AvailabilityZone",
                                               "OnDemandPrice",
                                               "PerfTtbarTotal"))

data_block = {
    "Nersc_Instance_Performance": nersc_instance_performance_df.reindex(columns=("EntryName",
                                                                                 "InstanceType",
                                                                                 "AvailabilityZone",
                                                                                 "OnDemandPrice",
                                                                                 "PerfTtbarTotal")),
    "Factory_Entries_LCF": pd.DataFrame([
        {"EntryName": "CMSHTPC_T3_US_NERSC_Cori",
         "GlideinConfigPerEntryMaxGlideins": 200,
         "GlideinMonitorTotalStatusRunning": 100,
         "GlideinConfigPerEntryMaxIdle": 10,
         "GlideinMonitorTotalStatusIdle": 10}]),
}

nersc_price_performance_df = pd.DataFrame([
    {"EntryName": "CMSHTPC_T3_US_NERSC_Cori",
     "PricePerformance": 0.6}])

expected_transform_output = {
    _produces[0]: nersc_price_performance_df.reindex(columns=("EntryName",
                                                              "PricePerformance")),
    _produces[1]: pd.DataFrame([
        {"EntryName": "CMSHTPC_T3_US_NERSC_Cori",
         "FigureOfMerit": 0.3
         }]),
}


class TestNerscFigureOfMerit:

    def test_produces(self):
        nersc_figure_of_merit = NerscFigureOfMerit.NerscFigureOfMerit(config)
        assert nersc_figure_of_merit._produces == produces

    def test_transform(self):
        nersc_figure_of_merit = NerscFigureOfMerit.NerscFigureOfMerit(config)
        res = nersc_figure_of_merit.transform(data_block)
        verify_products(nersc_figure_of_merit, res)
        for key, value in res.items():
            try:
                assert expected_transform_output[key].equals(value)
            except Exception:
                print(key, " fail\n",
                      expected_transform_output[key], "\n", value)
