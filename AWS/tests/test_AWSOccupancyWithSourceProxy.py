import os

import boto3
import mock
import pandas as pd

import decisionengine.framework.modules.SourceProxy as SourceProxy
import decisionengine_modules.AWS.sources.AWSOccupancyWithSourceProxy as Occupancy
import utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

config={"channel_name": "channel_aws_config_data",
                               "Dataproducts": ["spot_occupancy_config"],
                               "retries": 3,
                               "retry_timeout": 20,
    }

account = {'spot_occupancy_config': pd.read_csv(os.path.join(DATA_DIR,'account_config.csv'))}

expected_pandas_df = pd.read_csv(os.path.join(DATA_DIR,
                                              'AWSOcupancyWithSourceProxy_expected_acquire.csv'))

produces = ['AWS_Occupancy']


class SessionMock(object):
    def resource(self, service = None, region_name = None):
        return None


class TestAWSOccupancyWithSourceProxy:
    def test_produces(self):
        with mock.patch.object(SourceProxy.SourceProxy, "__init__", lambda x, y: None):
            aws_occ = Occupancy.AWSOccupancy(config)
            assert (aws_occ.produces() == produces)

    def test_acquire(self):
        with mock.patch.object(SourceProxy.SourceProxy, "__init__", lambda x, y: None):
            aws_occ = Occupancy.AWSOccupancy(config)
            with mock.patch.object(SourceProxy.SourceProxy, 'acquire') as acquire:
                acquire.return_value = account
                with mock.patch.object(boto3.session, 'Session') as s:
                    s.return_value = SessionMock()
                    with mock.patch.object(Occupancy.OccupancyForRegion, 'get_ec2_instances') as get_instances:
                        cap = utils.input_from_file(os.path.join(DATA_DIR,
                                                                 'occupancy.fixture'))
                        get_instances.return_value = cap
                        res = aws_occ.acquire()
                        assert produces == res.keys()
                        df1 = expected_pandas_df.sort_values(['AvailabilityZone', 'InstanceType'])
                        new_df = res.get(produces[0]).sort_values(['AvailabilityZone', 'InstanceType'])
                        new_df.reindex()
                        assert utils.compare_dfs(df1, new_df)
