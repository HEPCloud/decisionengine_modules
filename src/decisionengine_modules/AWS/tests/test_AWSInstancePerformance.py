# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

import pandas as pd
import pytest

import decisionengine_modules.AWS.sources.AWSInstancePerformance as AWSInstancePerformance

from decisionengine.framework.modules.Module import verify_products

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

config = {"channel_name": "test", "data_file": os.path.join(DATA_DIR, "instance_performance_sample.csv")}
expected_pandas_df = (
    pd.read_csv(config.get("data_file"))
    .drop_duplicates(subset=["AvailabilityZone", "InstanceType"], keep="last")
    .reset_index(drop=True)
)


@pytest.fixture
def aws_instance_performance():
    return AWSInstancePerformance.AWSInstancePerformance(config)


def test_produces(aws_instance_performance):
    assert aws_instance_performance._produces == {"Performance_Data": pd.DataFrame}


def test_acquire(aws_instance_performance):
    res = aws_instance_performance.acquire()
    verify_products(aws_instance_performance, res)
    assert expected_pandas_df.equals(res.get("Performance_Data"))
