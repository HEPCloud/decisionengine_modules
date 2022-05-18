# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

from unittest import mock

import boto3
import pandas as pd
import structlog

import decisionengine.framework.modules.Transform as Transform
import decisionengine_modules.AWS.transforms.AWSOccupancy as Occupancy

from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

config = {}

account = {"spot_occupancy_config": pd.read_csv(os.path.join(DATA_DIR, "account_config.csv"))}

expected_pandas_df = pd.read_csv(os.path.join(DATA_DIR, "AWSOccupancyTransform_expected_acquire.csv"))

consumes = {"spot_occupancy_config": pd.DataFrame}

produces = {"AWS_Occupancy": pd.DataFrame}


def transform_init_mock(s, p):
    s.logger = structlog.getLogger("test")


class SessionMock:
    def resource(self, service=None, region_name=None):
        return None


def test_consumes():
    with mock.patch.object(Transform.Transform, "__init__", transform_init_mock):
        aws_occ = Occupancy.AWSOccupancy(config)
        assert aws_occ._consumes == consumes


def test_produces():
    with mock.patch.object(Transform.Transform, "__init__", transform_init_mock):
        aws_occ = Occupancy.AWSOccupancy(config)
        assert aws_occ._produces == produces


def test_transform():
    with mock.patch.object(Transform.Transform, "__init__", transform_init_mock):
        aws_occ = Occupancy.AWSOccupancy(config)
        with mock.patch.object(boto3.session, "Session") as s:
            s.return_value = SessionMock()
            with mock.patch.object(Occupancy.OccupancyForRegion, "get_ec2_instances") as get_instances:
                cap = utils.input_from_file(os.path.join(DATA_DIR, "occupancy.fixture"))
                get_instances.return_value = cap
                res = aws_occ.transform(account)
                assert produces.keys() == res.keys()
                df1 = expected_pandas_df.sort_values(["AvailabilityZone", "InstanceType"])
                new_df = res.get("AWS_Occupancy").sort_values(["AvailabilityZone", "InstanceType"])
                new_df = new_df.reindex(df1.columns, axis=1)
                new_df = new_df.set_index(df1.index)
                pd.testing.assert_frame_equal(df1, new_df)
