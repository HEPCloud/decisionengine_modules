# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas as pd
import pytest

from decisionengine.framework.modules.Module import verify_products
from decisionengine_modules.NERSC.transforms import NerscFigureOfMerit

nersc_instance_performance_df = pd.DataFrame(
    [
        {
            "EntryName": "CMSHTPC_T3_US_NERSC_Cori",
            "InstanceType": "haswell",
            "AvailabilityZone": "cori",
            "OnDemandPrice": 0.576,
            "PerfTtbarTotal": 0.96,
        }
    ]
).reindex(columns=("EntryName", "InstanceType", "AvailabilityZone", "OnDemandPrice", "PerfTtbarTotal"))

data_block = {
    "Nersc_Instance_Performance": nersc_instance_performance_df.reindex(
        columns=("EntryName", "InstanceType", "AvailabilityZone", "OnDemandPrice", "PerfTtbarTotal")
    ),
    "Factory_Entries_LCF": pd.DataFrame(
        [
            {
                "EntryName": "CMSHTPC_T3_US_NERSC_Cori",
                "GlideinConfigPerEntryMaxGlideins": 200,
                "GlideinMonitorTotalStatusRunning": 100,
                "GlideinConfigPerEntryMaxIdle": 10,
                "GlideinMonitorTotalStatusIdle": 10,
            }
        ]
    ),
}

nersc_price_performance_df = pd.DataFrame([{"EntryName": "CMSHTPC_T3_US_NERSC_Cori", "PricePerformance": 0.6}])


@pytest.fixture
def nersc_figure_of_merit():
    return NerscFigureOfMerit.NerscFigureOfMerit({"channel_name": "test"})


def test_produces(nersc_figure_of_merit):
    produces = ["Nersc_Price_Performance", "Nersc_Figure_Of_Merit"]
    assert nersc_figure_of_merit._produces == dict.fromkeys(produces, pd.DataFrame)


def test_transform(nersc_figure_of_merit):
    expected_transform_output = {
        "Nersc_Price_Performance": nersc_price_performance_df.reindex(columns=("EntryName", "PricePerformance")),
        "Nersc_Figure_Of_Merit": pd.DataFrame([{"EntryName": "CMSHTPC_T3_US_NERSC_Cori", "FigureOfMerit": 0.3}]),
    }
    res = nersc_figure_of_merit.transform(data_block)
    verify_products(nersc_figure_of_merit, res)
    for key, value in res.items():
        try:
            assert expected_transform_output[key].equals(value)
        except Exception:
            print(key, " fail\n", expected_transform_output[key], "\n", value)
