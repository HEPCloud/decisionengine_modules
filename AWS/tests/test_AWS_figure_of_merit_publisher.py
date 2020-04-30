import os
import unittest

import pandas as pd

import decisionengine_modules.AWS.publishers.AWS_figure_of_merit as AWSFOMPublisher

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EXPECTED_REPLY = pd.read_csv(os.path.join(DATA_DIR,
                                          "expected_AWS_figure_of_merit_pub.csv"))
OUTPUT_FILE = "AWS_figure_of_merit_pub.csv"
CONSUMES = ["AWS_Figure_Of_Merit"]


def create_datablock():
    data_block = {}
    data_block['AWS_Figure_Of_Merit'] = pd.read_csv(os.path.join(DATA_DIR,
                                                                 'expected_figure_of_merit.csv'))
    return data_block


class TestAWSFOMPublisher(unittest.TestCase):

    def setUp(self):
        self.publisher = AWSFOMPublisher.AWSFOMPublisher({'publish_to_graphite': False,
                                                          'graphite_host': 'fifemondata.fnal.gov',
                                                          'graphite_port': 2104,
                                                          'graphite_context': 'hepcloud.aws',
                                                          'output_file': OUTPUT_FILE})

    def tearDown(self):
        try:
            os.unlink(OUTPUT_FILE)
        except OSError:
            pass

    def test_consumes(self):
        self.assertTrue(self.publisher.consumes() == CONSUMES)

    def test_transform(self):
        data_block = create_datablock()
        self.publisher.publish(data_block)
        opd = pd.read_csv(OUTPUT_FILE)
        self.assertTrue(opd.equals(EXPECTED_REPLY))
