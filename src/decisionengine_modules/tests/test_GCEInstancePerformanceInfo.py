import os

import pandas as pd

from decisionengine_modules.GCE.sources import GCEInstancePerformance
from decisionengine.framework.modules.Module import verify_products

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "instance_performance_google.csv")

CONFIG = {"channel_name": "test", "csv_file": CSV_FILE}

EXPECTED_PANDAS_DF = pd.read_csv(CONFIG.get("csv_file"))

_PRODUCES = {'GCE_Instance_Performance': pd.DataFrame}


class TestGCEInstancePerformance:

    def test_produces(self):
        gce_price_performance = GCEInstancePerformance.GCEInstancePerformance(CONFIG)
        assert gce_price_performance._produces == _PRODUCES

    def test_acquire(self):
        gce_price_performance = GCEInstancePerformance.GCEInstancePerformance(CONFIG)
        res = gce_price_performance.acquire()
        verify_products(gce_price_performance, res)
        assert EXPECTED_PANDAS_DF.equals(res.get('GCE_Instance_Performance'))
