import pandas as pd

from decisionengine_modules.GCE.sources import GCEPricePerformance

config = {
    "csv_file": "price_performance_gce.csv",
}

expected_pandas_df = pd.read_csv(config.get("csv_file"))

produces = ['GCE_Price_Performance']


class TestGCEPricePerformance:

    def test_produces(self):
        gce_price_performance = GCEPricePerformance.GCEPricePerformance(config)
        assert gce_price_performance.produces() == produces

    def test_acquire(self):
        gce_price_performance = GCEPricePerformance.GCEPricePerformance(config)
        res = gce_price_performance.acquire()
        assert produces == res.keys()
        assert expected_pandas_df.equals(res.get(produces[0]))
