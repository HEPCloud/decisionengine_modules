# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

import pandas as pd

from decisionengine.framework.modules.Module import verify_products
from decisionengine_modules.GCE.sources import GCEInstancePerformance

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "instance_performance_google.csv")

CONFIG = {"channel_name": "test", "csv_file": CSV_FILE}

EXPECTED_PANDAS_DF = pd.read_csv(CONFIG.get("csv_file"))

_PRODUCES = {"GCE_Instance_Performance": pd.DataFrame}

LOGGER = None


def test_produces():
    gce_price_performance = GCEInstancePerformance.GCEInstancePerformance(CONFIG, LOGGER)
    assert gce_price_performance._produces == _PRODUCES


def test_acquire():
    gce_price_performance = GCEInstancePerformance.GCEInstancePerformance(CONFIG, LOGGER)
    res = gce_price_performance.acquire()
    verify_products(gce_price_performance, res)
    assert EXPECTED_PANDAS_DF.equals(res.get("GCE_Instance_Performance"))
