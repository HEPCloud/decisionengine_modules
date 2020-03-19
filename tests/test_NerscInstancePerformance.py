import os

import pandas as pd

from decisionengine_modules.NERSC.sources import NerscInstancePerformance

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "instance_performance_nersc.csv")

CONFIG = {
    "csv_file": CSV_FILE,
}

EXPECTED_PANDAS_DF = pd.read_csv(CONFIG.get("csv_file"))

PRODUCES = ['Nersc_Instance_Performance']


class TestNerscInstancePerformance:

    def test_produces(self):
        nersc_instance_performance = NerscInstancePerformance.NerscInstancePerformance(CONFIG)
        assert nersc_instance_performance.produces() == PRODUCES

    def test_acquire(self):
        nersc_instance_performance = NerscInstancePerformance.NerscInstancePerformance(CONFIG)
        res = nersc_instance_performance.acquire()
        assert PRODUCES == list(res.keys())
        assert EXPECTED_PANDAS_DF.equals(res.get(PRODUCES[0]))
