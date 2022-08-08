# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

import numpy as np
import pandas as pd
import tabulate

from decisionengine_modules.GCE.transforms import GceFigureOfMerit
from decisionengine_modules.tests.dataframe_for_entrytype import dataframe_for_entrytype

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "GceOccupancy.output.fixture.csv")

_PRODUCES = ["GCE_Price_Performance", "GCE_Figure_Of_Merit"]
_PRODUCES_DICT = dict.fromkeys(_PRODUCES, pd.DataFrame)
CONFIG = {"channel_name": "test"}

GCE_OCCUPANCY_DF = pd.read_csv(CSV_FILE)

gce_instance_performance_df = pd.DataFrame(
    [
        {
            "EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
            "InstanceType": "n1-standard-1",
            "AvailabilityZone": "us-central1-a",
            "OnDemandPrice": 0.0475,
            "PerfTtbarTotal": 0.0317,
        },
    ]
)

gce_instance_performance_df.reindex(
    columns=("EnryName", "InstanceType", "AvailabilityZone", "OnDemandPrice", "PerfTtbarTotal")
)

# expected datablock
data_block = {
    "GCE_Instance_Performance": gce_instance_performance_df.reindex(
        columns=("EntryName", "InstanceType", "AvailabilityZone", "OnDemandPrice", "PerfTtbarTotal")
    ),
    "Factory_Entries": dataframe_for_entrytype(
        key="GCE",
        data=[
            {
                "EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
                "GlideinConfigPerEntryMaxIdle": 100,
                "GlideinMonitorTotalStatusIdle": 10,
                "GlideinConfigPerEntryMaxGlideins": 200,
                "GlideinMonitorTotalStatusRunning": 100,
            }
        ],
    ),
    "GCE_Occupancy": GCE_OCCUPANCY_DF,
}

gce_price_performance_df = pd.DataFrame(
    [
        {"EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1", "PricePerformance": 1.498423},
    ]
)

expected_transform_output = {
    _PRODUCES[0]: gce_price_performance_df.reindex(columns=("EntryName", "PricePerformance")),
    _PRODUCES[1]: pd.DataFrame(
        [
            {"EntryName": "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1", "FigureOfMerit": 0.08241324921135648},
        ]
    ),
}

for _k, value in data_block.items():
    print(tabulate.tabulate(value, headers="keys", tablefmt="psql"))


def test_produces():
    gce_figure_of_merit = GceFigureOfMerit.GceFigureOfMerit(CONFIG)
    assert gce_figure_of_merit._produces == _PRODUCES_DICT


def test_transform():
    gce_figure_of_merit = GceFigureOfMerit.GceFigureOfMerit(CONFIG)
    res = gce_figure_of_merit.transform(data_block)
    assert _PRODUCES.sort() == list(res.keys()).sort()

    expected_df = expected_transform_output[_PRODUCES[0]]
    res_df = res[_PRODUCES[0]]
    assert np.isclose(expected_df["FigureOfMerit"], res_df["FigureOfMerit"])

    expected_df = expected_transform_output[_PRODUCES[1]]
    res_df = res[_PRODUCES[1]]
    assert np.isclose(expected_df["PricePerformance"], res_df["PricePerformance"])
