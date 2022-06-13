# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

from unittest import mock

import boto3
import numpy
import pandas as pd
import pytest
import structlog

import decisionengine.framework.modules.Transform as Transform
import decisionengine_modules.AWS.transforms.AWSSpotPrice as AWSSpotPrice

from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

account = {"spot_occupancy_config": pd.read_csv(os.path.join(DATA_DIR, "account_config.csv"))}

expected_pandas_df = pd.read_csv(
    os.path.join(DATA_DIR, "AWSSpotPriceTransform_expected_acquire.csv"), float_precision="high"
)

consumes = {"spot_occupancy_config": pd.DataFrame}

produces = {"provisioner_resource_spot_prices": pd.DataFrame}


def transform_init_mock(s, p):
    s.logger = structlog.getLogger("test")


@pytest.fixture
def aws_spot_price():
    with mock.patch.object(Transform.Transform, "__init__", transform_init_mock):
        yield AWSSpotPrice.AWSSpotPrice({})


def fix_spot_price(df):
    out_df = df.copy(deep=True)
    for r, row in df.iterrows():
        if isinstance(row["SpotPrice"], str):
            out_df.loc[r, "SpotPrice"] = numpy.float64(row["SpotPrice"])
    return out_df


class SessionMock:
    def client(self, service=None, region_name=None):
        return None


def test_consumes(aws_spot_price):
    assert aws_spot_price._consumes == consumes


def test_produces(aws_spot_price):
    assert aws_spot_price._produces == produces


def test_transform(aws_spot_price):
    with mock.patch.object(boto3.session, "Session", return_value=SessionMock()), mock.patch.object(
        AWSSpotPrice.AWSSpotPriceForRegion,
        "get_price",
        return_value=utils.input_from_file(os.path.join(DATA_DIR, "spot_price.fixture")),
    ):
        res = aws_spot_price.transform(account)
        assert produces.keys() == res.keys()
        new_df = fix_spot_price(res["provisioner_resource_spot_prices"])
        expected_pandas_df2 = expected_pandas_df.astype("object")
        pd.testing.assert_frame_equal(expected_pandas_df2, new_df)
