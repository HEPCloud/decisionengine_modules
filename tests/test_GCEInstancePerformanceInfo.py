import os

import pandas as pd

from decisionengine_modules.GCE.sources import GCEInstancePerformance

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "instance_performance_google.csv")

CONFIG = {
    "csv_file": CSV_FILE,
}

EXPECTED_PANDAS_DF = pd.read_csv(CONFIG.get("csv_file"))

PRODUCES = ['GCE_Instance_Performance']


class TestGCEInstancePerformance:

    def test_produces(self):
        gce_price_performance = GCEInstancePerformance.GCEInstancePerformance(CONFIG)
        assert gce_price_performance.produces() == PRODUCES

    def test_acquire(self):
        gce_price_performance = GCEInstancePerformance.GCEInstancePerformance(CONFIG)
        res = gce_price_performance.acquire()
        assert PRODUCES == list(res.keys())
        assert EXPECTED_PANDAS_DF.equals(res.get(PRODUCES[0]))
