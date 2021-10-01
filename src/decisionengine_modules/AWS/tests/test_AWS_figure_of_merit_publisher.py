import contextlib
import os
import unittest

import pandas as pd

import decisionengine_modules.AWS.publishers.AWS_figure_of_merit as AWSFOMPublisher

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

try:
    # pandas 1.2 uses a new method for floats, use the "legacy" one for now
    # https://pandas.pydata.org/pandas-docs/stable/whatsnew/v1.2.0.html#change-in-default-floating-precision-for-read-csv-and-read-table
    EXPECTED_REPLY = pd.read_csv(
        os.path.join(DATA_DIR, "expected_AWS_figure_of_merit_pub.csv"), float_precision="legacy"
    )
except TypeError:
    EXPECTED_REPLY = pd.read_csv(os.path.join(DATA_DIR, "expected_AWS_figure_of_merit_pub.csv"))
OUTPUT_FILE = "AWS_figure_of_merit_pub.csv"


def create_datablock():
    data_block = {"channel_name": "test"}
    try:
        # pandas 1.2 uses a new method for floats, use the "legacy" one for now
        # https://pandas.pydata.org/pandas-docs/stable/whatsnew/v1.2.0.html#change-in-default-floating-precision-for-read-csv-and-read-table
        data_block["AWS_Figure_Of_Merit"] = pd.read_csv(
            os.path.join(DATA_DIR, "expected_figure_of_merit.csv"), float_precision="legacy"
        )
    except TypeError:
        data_block["AWS_Figure_Of_Merit"] = pd.read_csv(os.path.join(DATA_DIR, "expected_figure_of_merit.csv"))
    return data_block


class TestAWSFOMPublisher(unittest.TestCase):
    def setUp(self):
        self.publisher = AWSFOMPublisher.AWSFOMPublisher(
            {
                "publish_to_graphite": False,
                "graphite_host": "fifemondata.fnal.gov",
                "graphite_port": 2104,
                "graphite_context": "hepcloud.aws",
                "output_file": OUTPUT_FILE,
                "channel_name": "test",
            }
        )

    def tearDown(self):
        with contextlib.suppress(OSError):
            os.unlink(OUTPUT_FILE)

    def test_consumes(self):
        assert self.publisher._consumes == {"AWS_Figure_Of_Merit": pd.DataFrame}

    def test_transform(self):
        data_block = create_datablock()
        self.publisher.publish(data_block)
        try:
            # pandas 1.2 uses a new method for floats, use the "legacy" one for now
            # https://pandas.pydata.org/pandas-docs/stable/whatsnew/v1.2.0.html#change-in-default-floating-precision-for-read-csv-and-read-table
            opd = pd.read_csv(OUTPUT_FILE, float_precision="legacy")
        except TypeError:
            opd = pd.read_csv(OUTPUT_FILE)

        assert opd.to_csv() == EXPECTED_REPLY.to_csv()
