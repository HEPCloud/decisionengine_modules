# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pandas as pd
import pytest

from decisionengine.framework.modules.Module import verify_products
from decisionengine_modules.AWS.transforms import AwsBurnRate

occupancy = pd.DataFrame(
    {
        "AccountName": "FERMILAB",
        "AvailabilityZone": "us-east-1a",
        "InstanceType": ["c3.xlarge", "t2.micro"],
        "RunningVms": [10, 1],
    }
)

provisioner_resource_spot_prices = pd.DataFrame(
    [
        {
            "AccountName": "CMS",
            "AvailabilityZone": "us-east-1c",
            "InstanceType": "m3.xlarge",
            "ProductDescription": "Linux/UNIX",
            "SpotPrice": 0.0644,
            "Timestamp": pd.Timestamp("2019-01-25 11:15:22"),
        },
        {
            "AccountName": "CMS",
            "AvailabilityZone": "us-east-1a",
            "InstanceType": "m3.2xlarge",
            "ProductDescription": "Linux/UNIX",
            "SpotPrice": 0.1353,
            "Timestamp": pd.Timestamp("2019-01-25 08:02:48"),
        },
        {
            "AccountName": "FERMILAB",
            "AvailabilityZone": "us-east-1b",
            "InstanceType": "m3.xlarge",
            "ProductDescription": "Linux/UNIX",
            "SpotPrice": 0.0682,
            "Timestamp": pd.Timestamp("2019-01-25 12:05:25"),
        },
        {
            "AccountName": "FERMILAB",
            "AvailabilityZone": "us-east-1e",
            "InstanceType": "m3.xlarge",
            "ProductDescription": "Linux/UNIX",
            "SpotPrice": 0.0635,
            "Timestamp": pd.Timestamp("2019-01-25 11:15:22"),
        },
        {
            "AccountName": "FERMILAB",
            "AvailabilityZone": "us-east-1a",
            "InstanceType": "c3.xlarge",
            "ProductDescription": "Linux/UNIX",
            "SpotPrice": 0.0682,
            "Timestamp": pd.Timestamp("2019-01-25 12:05:25"),
        },
        {
            "AccountName": "FERMILAB",
            "AvailabilityZone": "us-east-1a",
            "InstanceType": "t2.micro",
            "ProductDescription": "Linux/UNIX",
            "SpotPrice": 0.0635,
            "Timestamp": pd.Timestamp("2019-01-25 11:15:22"),
        },
    ]
)

df = pd.merge(
    occupancy, provisioner_resource_spot_prices, how="inner", on=["AccountName", "AvailabilityZone", "InstanceType"]
)


data_block = {
    "provisioner_resource_spot_prices": provisioner_resource_spot_prices,
    "AWS_Occupancy": occupancy,
}

expected_transform_output = {"AWS_Burn_Rate": pd.DataFrame([{"BurnRate": 0.7455}])}


@pytest.fixture
def aws_burn_rate():
    config = {"channel_name": "test"}
    return AwsBurnRate.AwsBurnRate(config)


def test_produces(aws_burn_rate):
    assert aws_burn_rate._produces == {"AWS_Burn_Rate": pd.DataFrame}


def test_transform(aws_burn_rate):
    res = aws_burn_rate.transform(data_block)
    verify_products(aws_burn_rate, res)

    expected_df = expected_transform_output["AWS_Burn_Rate"]
    res_df = res["AWS_Burn_Rate"]
    assert np.isclose(expected_df["BurnRate"], res_df["BurnRate"])
