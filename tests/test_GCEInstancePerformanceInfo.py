import pandas as pd

from decisionengine_modules.GCE.sources import GCEInstancePerformance

config = {
    "csv_file": "instance_performance_google.csv",
}

expected_pandas_df = pd.read_csv(config.get("csv_file"))

produces = ['GCE_Instance_Performance']


class TestGCEInstancePerformance:

    def test_produces(self):
        gce_price_performance = GCEInstancePerformance.GCEInstancePerformance(config)
        assert gce_price_performance.produces() == produces

    def test_acquire(self):
        gce_price_performance = GCEInstancePerformance.GCEInstancePerformance(config)
        res = gce_price_performance.acquire()
        assert produces == res.keys()
        assert expected_pandas_df.equals(res.get(produces[0]))
