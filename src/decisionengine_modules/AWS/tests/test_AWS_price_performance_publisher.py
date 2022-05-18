# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import contextlib
import os

import pandas as pd
import pytest

import decisionengine_modules.AWS.publishers.AWS_price_performance as AWSPPublisher

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = "AWS_price_perf_pub.csv"

EXPECTED_REPLY = pd.read_csv(os.path.join(DATA_DIR, "expected_AWS_price_perf_pub.csv"))


def create_datablock():
    data_block = {"channel_name": "test"}
    data_block["AWS_Price_Performance"] = pd.read_csv(os.path.join(DATA_DIR, "expected_price_performance.csv"))
    return data_block


@pytest.fixture(scope="module")
def publisher_instance():
    publisher = AWSPPublisher.AWSPricePerformancePublisher(
        {
            "publish_to_graphite": False,
            "graphite_host": "fifemondata.fnal.gov",
            "graphite_port": 2104,
            "graphite_context": "hepcloud.aws",
            "output_file": OUTPUT_FILE,
            "channel_name": "test",
        }
    )
    yield publisher
    with contextlib.suppress(OSError):
        os.unlink(OUTPUT_FILE)


def test_consumes(publisher_instance):
    assert publisher_instance._consumes == {"AWS_Price_Performance": pd.DataFrame}


def test_transform(publisher_instance):
    data_block = create_datablock()
    publisher_instance.publish(data_block)
    opd = pd.read_csv(OUTPUT_FILE)
    assert opd.equals(EXPECTED_REPLY)
