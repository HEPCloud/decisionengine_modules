import pandas as pd

from decisionengine_modules.NERSC.sources import NerscInstancePerformance

config = {
    "csv_file": "instance_performance_nersc.csv",
}

expected_pandas_df = pd.read_csv(config.get("csv_file"))

produces = ['Nersc_Instance_Performance']


class TestNerscInstancePerformance:

    def test_produces(self):
        nersc_instance_performance = NerscInstancePerformance.NerscInstancePerformance(config)
        assert nersc_instance_performance.produces() == produces

    def test_acquire(self):
        nersc_instance_performance = NerscInstancePerformance.NerscInstancePerformance(config)
        res = nersc_instance_performance.acquire()
        assert produces == res.keys()
        assert expected_pandas_df.equals(res.get(produces[0]))