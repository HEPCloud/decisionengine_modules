# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas as pd
import pytest

from decisionengine.framework.modules.Module import verify_products
from decisionengine_modules.NERSC.transforms import NerscFigureOfMerit
from decisionengine_modules.tests.dataframe_for_entrytype import dataframe_for_entrytype

data_block = {
    "Nersc_Instance_Performance": pd.DataFrame(
        [
            {
                "EntryName": "CMSHTPC_T3_US_NERSC_Cori",
                "InstanceType": "haswell",
                "AvailabilityZone": "cori",
                "OnDemandPrice": 0.576,
                "PerfTtbarTotal": 0.96,
            }
        ]
    ),
    "Factory_Entries": dataframe_for_entrytype(
        key="LCF",
        data=[
            {
                "EntryName": "CMSHTPC_T3_US_NERSC_Cori",
                "GlideinConfigPerEntryMaxGlideins": 200,
                "GlideinMonitorTotalStatusRunning": 99,
                "GlideinConfigPerEntryMaxIdle": 10,
                "GlideinMonitorTotalStatusIdle": 9,
            }
        ],
    ),
}


@pytest.fixture
def nersc_figure_of_merit():
    return NerscFigureOfMerit.NerscFigureOfMerit({"channel_name": "test"})


def test_produces(nersc_figure_of_merit):
    produces = ["Nersc_Price_Performance", "Nersc_Figure_Of_Merit"]
    assert nersc_figure_of_merit._produces == dict.fromkeys(produces, pd.DataFrame)


def test_transform(nersc_figure_of_merit):
    expected_transform_output = {
        "Nersc_Price_Performance": pd.DataFrame([{"EntryName": "CMSHTPC_T3_US_NERSC_Cori", "PricePerformance": 0.6}]),
        "Nersc_Figure_Of_Merit": pd.DataFrame([{"EntryName": "CMSHTPC_T3_US_NERSC_Cori", "FigureOfMerit": 0.3}]),
    }
    res = nersc_figure_of_merit.transform(data_block)
    verify_products(nersc_figure_of_merit, res)
    for key, value in res.items():
        assert expected_transform_output[key].equals(value)
