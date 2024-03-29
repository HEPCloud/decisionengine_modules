# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

import pandas as pd

from decisionengine.framework.modules.Module import verify_products
from decisionengine_modules.NERSC.sources import NerscInstancePerformance

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "instance_performance_nersc.csv")

CONFIG = {
    "channel_name": "test",
    "csv_file": CSV_FILE,
}

EXPECTED_PANDAS_DF = pd.read_csv(CONFIG.get("csv_file"))

_PRODUCES = {"Nersc_Instance_Performance": pd.DataFrame}


def test_produces():
    nersc_instance_performance = NerscInstancePerformance.NerscInstancePerformance(CONFIG)
    assert nersc_instance_performance._produces == _PRODUCES


def test_acquire():
    nersc_instance_performance = NerscInstancePerformance.NerscInstancePerformance(CONFIG)
    res = nersc_instance_performance.acquire()
    verify_products(nersc_instance_performance, res)
    assert EXPECTED_PANDAS_DF.equals(res.get("Nersc_Instance_Performance"))
