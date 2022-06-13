# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

from unittest import mock

import boto3
import pandas as pd
import pytest
import structlog

import decisionengine.framework.modules.Transform as Transform
import decisionengine_modules.AWS.transforms.AWSOccupancy as Occupancy

from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

account = {"spot_occupancy_config": pd.read_csv(os.path.join(DATA_DIR, "account_config.csv"))}

expected_pandas_df = pd.read_csv(os.path.join(DATA_DIR, "AWSOccupancyTransform_expected_acquire.csv"))

consumes = {"spot_occupancy_config": pd.DataFrame}

produces = {"AWS_Occupancy": pd.DataFrame}


def transform_init_mock(s, p):
    s.logger = structlog.getLogger("test")


@pytest.fixture
def aws_occupancy():
    with mock.patch.object(Transform.Transform, "__init__", transform_init_mock):
        yield Occupancy.AWSOccupancy({})


class SessionMock:
    def resource(self, service=None, region_name=None):
        return None


def test_consumes(aws_occupancy):
    assert aws_occupancy._consumes == consumes


def test_produces(aws_occupancy):
    assert aws_occupancy._produces == produces


def test_transform(aws_occupancy):
    with mock.patch.object(boto3.session, "Session", return_value=SessionMock()), mock.patch.object(
        Occupancy.OccupancyForRegion,
        "get_ec2_instances",
        return_value=utils.input_from_file(os.path.join(DATA_DIR, "occupancy.fixture")),
    ):
        res = aws_occupancy.transform(account)
        assert produces.keys() == res.keys()
        df1 = expected_pandas_df.sort_values(["AvailabilityZone", "InstanceType"])
        new_df = res.get("AWS_Occupancy").sort_values(["AvailabilityZone", "InstanceType"])
        new_df = new_df.reindex(df1.columns, axis=1)
        new_df = new_df.set_index(df1.index)
        pd.testing.assert_frame_equal(df1, new_df)
