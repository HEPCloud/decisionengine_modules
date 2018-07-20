import pandas as pd

from decisionengine_modules.NERSC.transforms import NerscFigureOfMerit

"""
IMPORTANT: Please do not change order of these keys and always 
           append new keys rather than pre-pend or insert:
"""
produces = ['Nersc_Price_Performance', 'Nersc_Figure_Of_Merit']


config = {
    "entry_name_mapping": {
        "T3_US_NERSC_Cori": "haswell,cori",
        "T3_US_NERSC_Cori_shared": "haswell_shared,cori",
        "T3_US_NERSC_Cori_KNL": "knl,cori",
        "T3_US_NERSC_Edison": "haswell,edison",
    },
}

nersc_instance_performance_df =  pd.DataFrame([
        {"InstanceType": "haswell",
         "AvailabilityZone": "cori",
         "OnDemandPrice": 0.576,
         "PerfTtbarTotal": 0.96}, ])

data_block = {
    "Nersc_Instance_Performance": nersc_instance_performance_df.reindex(columns=("InstanceType",
                                                                                 "AvailabilityZone",
                                                                                 "OnDemandPrice",
                                                                                 "PerfTtbarTotal")),
    "Factory_Entries_LCF": pd.DataFrame([
        {"EntryName": "CMSHTPC_T3_US_NERSC_Cori",
         "GlideinConfigPerEntryMaxGlideins": 200,
         "GlideinMonitorTotalStatusRunning": 100}, ]),
}

nersc_price_performance_df = pd.DataFrame([
    {"InstanceType": "haswell",
     "AvailabilityZone": "cori",
     "PricePerformance": 0.6}, ])

expected_transform_output = {
    produces[0]: nersc_price_performance_df.reindex(columns=("InstanceType",
                                                             "AvailabilityZone",
                                                             "PricePerformance")),
    produces[1]: pd.DataFrame([
        {"EntryName": "CMSHTPC_T3_US_NERSC_Cori",
         "FigureOfMerit": 0.3
        }, ]),
}


class TestNerscFigureOfMerit:

    def test_produces(self):
        nersc_figure_of_merit = NerscFigureOfMerit.NerscFigureOfMerit(config)
        assert nersc_figure_of_merit.produces() == produces

    def test_transform(self):
        nersc_figure_of_merit = NerscFigureOfMerit.NerscFigureOfMerit(config)
        res = nersc_figure_of_merit.transform(data_block)
        assert produces == res.keys()
        for key, value in res.items():
            assert expected_transform_output[key].equals(value)
