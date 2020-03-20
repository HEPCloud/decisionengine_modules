import os
import six
import unittest

import pandas as pd

import decisionengine_modules.AWS.publishers.AWS_price_performance as AWSPPublisher

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = "AWS_price_perf_pub.csv"

EXPECTED_REPLY = pd.read_csv(os.path.join(DATA_DIR,
                                          "expected_AWS_price_perf_pub.csv"))
CONSUMES = ["AWS_Price_Performance"]


def create_datablock():
    data_block = {}
    data_block['AWS_Price_Performance'] = pd.read_csv(
        os.path.join(DATA_DIR, 'expected_price_performance.csv'))
    return data_block


class TestAWSPPPublisher(unittest.TestCase):

    def setUp(self):
        self.publisher = AWSPPublisher.AWSPricePerformancePublisher({'publish_to_graphite': False,
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


if __name__ == '__main__':
    unittest.main()
