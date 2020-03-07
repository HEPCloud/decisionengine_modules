import numpy as np
import pandas as pd

from decisionengine_modules.AWS.transforms import AwsBurnRate

produces = ["AWS_Burn_Rate"]

config = {
}

occupancy = pd.DataFrame([
    {
        "AccountName": "FERMILAB",
        "AvailabilityZone": "us-east-1a",
        "InstanceType": "c3.xlarge",
        "RunningVms": 10,
    },
    {
        "AccountName": "FERMILAB",
        "AvailabilityZone": "us-east-1a",
        "InstanceType": "t2.micro",
        "RunningVms": 1,
    },
])

provisioner_resource_spot_prices = pd.DataFrame([
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
])

df = pd.merge(occupancy,
              provisioner_resource_spot_prices,
              how="inner",
              on=["AccountName", "AvailabilityZone", "InstanceType"])


data_block = {
    "provisioner_resource_spot_prices": provisioner_resource_spot_prices,
    "AWS_Occupancy": occupancy,
}

expected_transform_output = {
    produces[0]: pd.DataFrame([{
        "BurnRate": 0.7455}])
}


class TestAwsBurnRate:

    def test_produces(self):
        aws_burn_rate = AwsBurnRate.AwsBurnRate(config)
        assert aws_burn_rate.produces() == produces

    def test_transform(self):
        aws_burn_rate = AwsBurnRate.AwsBurnRate(config)
        res = aws_burn_rate.transform(data_block)
        assert produces.sort() == res.keys().sort()

        expected_df = expected_transform_output[produces[0]]
        res_df = res[produces[0]]
        assert np.isclose(expected_df["BurnRate"],
                          res_df["BurnRate"])
