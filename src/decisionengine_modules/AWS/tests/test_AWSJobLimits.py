# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

import pandas as pd

import decisionengine_modules.AWS.sources.AWSJobLimits as AWSJobLimits

from decisionengine.framework.modules.Module import verify_products

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

config = {"channel_name": "test", "data_file": os.path.join(DATA_DIR, "job_limits_sample.csv")}

expected_pandas_df = (
    pd.read_csv(config.get("data_file"))
    .drop_duplicates(subset=["AvailabilityZone", "InstanceType"], keep="last")
    .reset_index(drop=True)
)
produces = {"Job_Limits": pd.DataFrame}


def test_produces():
    aws_job_limits = AWSJobLimits.AWSJobLimits(config)
    assert aws_job_limits._produces == produces


def test_acquire():
    aws_job_limits = AWSJobLimits.AWSJobLimits(config)
    res = aws_job_limits.acquire()
    verify_products(aws_job_limits, res)
    assert expected_pandas_df.equals(res.get("Job_Limits"))
