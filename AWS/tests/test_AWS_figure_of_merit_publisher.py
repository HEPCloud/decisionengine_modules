import pandas as pd
import numpy
import os

import utils
import decisionengine_modules.AWS.publishers.AWS_figure_of_merit as AWSFOMPublisher

expected_reply = pd.read_csv('expected_AWS_figure_of_merit_pub.csv')
 
consumes = ['AWS_Figure_Of_Merit']

def create_datablock():
    data_block = {}
    data_block['AWS_Figure_Of_Merit'] =  pd.read_csv('expected_figure_of_merit.csv')
    return data_block

class TestAWSFOMPublisher:

    def test_consumes(self):
        fom_p = AWSFOMPublisher.AWSFOMPublisher({'publish_to_graphite': False,
                                                'graphite_host': 'fifemondata.fnal.gov',
                                                'graphite_port': 2104,
                                                'graphite_context':'hepcloud.aws',
                                                'output_file': 'AWS_figure_of_merit_pub.csv'})

        assert fom_p.consumes() == consumes

    def test_transform(self):
        fom_p = AWSFOMPublisher.AWSFOMPublisher({'publish_to_graphite': False,
                                                'graphite_host': 'fifemondata.fnal.gov',
                                                'graphite_port': 2104,
                                                'graphite_context':'hepcloud.aws',
                                                'output_file': 'AWS_figure_of_merit_pub.csv'})

        data_block = create_datablock()
        res = fom_p.publish(data_block)
        opd = pd.read_csv('AWS_figure_of_merit_pub.csv')
        assert opd.equals(expected_reply)

