import os

import pandas as pd

from decisionengine_modules.NERSC.sources import NerscInstancePerformance
from decisionengine.framework.modules.Module import verify_products

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "instance_performance_nersc.csv")

CONFIG = {
    "csv_file": CSV_FILE,
}

EXPECTED_PANDAS_DF = pd.read_csv(CONFIG.get("csv_file"))

_PRODUCES = {'Nersc_Instance_Performance': pd.DataFrame}


class TestNerscInstancePerformance:

    def test_produces(self):
        nersc_instance_performance = NerscInstancePerformance.NerscInstancePerformance(CONFIG)
        assert nersc_instance_performance._produces == _PRODUCES

    def test_acquire(self):
        nersc_instance_performance = NerscInstancePerformance.NerscInstancePerformance(CONFIG)
        res = nersc_instance_performance.acquire()
        verify_products(nersc_instance_performance, res)
        assert EXPECTED_PANDAS_DF.equals(res.get('Nersc_Instance_Performance'))
