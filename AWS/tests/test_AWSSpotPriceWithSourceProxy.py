import os

import boto3
import mock
import numpy
import pandas as pd

import decisionengine.framework.modules.SourceProxy as SourceProxy
import decisionengine_modules.AWS.sources.AWSSpotPriceWithSourceProxy as AWSSpotPrice
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

config = {"channel_name": "channel_aws_config_data",
                               "Dataproducts": ["spot_occupancy_config"],
                               "retries": 3,
                               "retry_timeout": 20,
    }

account = {'spot_occupancy_config': pd.read_csv(os.path.join(DATA_DIR,
                                                             'account_config.csv'))}

expected_pandas_df = pd.read_csv(os.path.join(DATA_DIR,
                                              'AWSSpotPriceWithSourceProxy_expected_acquire.csv'),
                                 float_precision='high')

produces = ['provisioner_resource_spot_prices']


def fix_spot_price(df):
    out_df = df.copy(deep=True)
    for r, row in df.iterrows():
        if isinstance(row['SpotPrice'], str):
            out_df.loc[r,'SpotPrice'] = numpy.float64(row['SpotPrice'])
    return out_df


class SessionMock(object):
    def client(self, service = None, region_name = None):
        return None


class TestAWSSpotPriceWithSourceProxy:
    def test_produces(self):
        with mock.patch.object(SourceProxy.SourceProxy, "__init__", lambda x, y: None):
            aws_s_p = AWSSpotPrice.AWSSpotPrice(config)
            assert (aws_s_p.produces('a') == produces)
    
    def test_acquire(self):
        with mock.patch.object(SourceProxy.SourceProxy, "__init__", lambda x, y: None):
            aws_s_p = AWSSpotPrice.AWSSpotPrice(config)
            with mock.patch.object(SourceProxy.SourceProxy, 'acquire') as acquire:
                acquire.return_value = account
                with mock.patch.object(boto3.session, 'Session') as s:
                    s.return_value = SessionMock()
                    with mock.patch.object(AWSSpotPrice.AWSSpotPriceForRegion, 'get_price') as get_price:
                        sp_d = utils.input_from_file(os.path.join(DATA_DIR,
                                                                  'spot_price.fixture'))
                        get_price.return_value = sp_d
                        res = aws_s_p.acquire()
                        assert produces == res.keys()
                        new_df = fix_spot_price(res[produces[0]])
                        assert utils.compare_dfs(expected_pandas_df, new_df)
