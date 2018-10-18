import pandas as pd
import numpy

import utils
import decisionengine_modules.AWS.transforms.FigureOfMerit as FigureOfMerit

expected_reply = {'AWS_Figure_Of_Merit': pd.read_csv('expected_figure_of_merit.csv'),
                  'AWS_Price_Performance': pd.read_csv('expected_price_performance.csv')
                  }
consumes = ['provisioner_resource_spot_prices',
          'Performance_Data',
          'Job_Limits', 'AWS_Occupancy']

#produces = ['AWS_Figure_Of_Merit', 'AWS_Price_Performance']
produces = ['AWS_Price_Performance', 'AWS_Figure_Of_Merit']

def create_datablock():
    data_block = {}
    data_block['provisioner_resource_spot_prices'] =  pd.read_csv('AWSSpotPriceWithSourceProxy_expected_acquire.csv', float_precision='high')
    data_block['Performance_Data'] = pd.read_csv('instance_performance_sample.csv').drop_duplicates(subset=[ 'AvailabilityZone', 'InstanceType'], keep='last').reset_index(drop = True)
    data_block['Job_Limits'] = pd.read_csv('job_limits.csv').drop_duplicates(subset=['AvailabilityZone', 'InstanceType'], keep='last').reset_index(drop=True)
    data_block['AWS_Occupancy'] = pd.read_csv('AWSOcupancyWithSourceProxy_expected_acquire.csv')
    return data_block

def fix_column(df, column):
    out_df = df.copy(deep=True)
    for r, row in df.iterrows():
        out_df.loc[r,column] = '%f'%(row[column],)
    return out_df

class TestFigureOfMerit:

    def test_consumes(self):
        fom = FigureOfMerit.FigureOfMerit()
        assert fom.consumes() == consumes

    def test_produces(self):
        fom = FigureOfMerit.FigureOfMerit()
        assert fom.produces() == produces

    def test_transform(self):
        fom = FigureOfMerit.FigureOfMerit()
        data_block = create_datablock()
        res = fom.transform(data_block)
        r_keys = res.keys().sort()
        p_keys = produces.sort()
        assert p_keys == r_keys
        for k in expected_reply.keys():
            if k == 'AWS_Price_Performance':
                df = fix_column(res[k], 'AWS_Price_Performance')
                edf = fix_column(expected_reply[k], 'AWS_Price_Performance')
            else:
                df = fix_column(res[k], 'AWS_Figure_Of_Merit')
                edf = fix_column(expected_reply[k], 'AWS_Figure_Of_Merit')
            assert utils.compare_dfs(edf, df)

