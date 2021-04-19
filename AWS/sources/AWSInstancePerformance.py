"""
Fill in data from Instance Performance CSV file
"""
import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter


@Source.supports_config(Parameter('data_file', type=str, comment="CSV cost data file"))
@Source.produces(Performance_Data=pd.DataFrame)
class AWSInstancePerformance(Source.Source):
    def __init__(self, config):
        self.data_file = config.get('data_file')

    def acquire(self):
        dataframe = pd.read_csv(self.data_file).drop_duplicates(subset=['AvailabilityZone',
                                                                        'InstanceType'],
                                                                keep='last').reset_index(drop=True)
        return {'Performance_Data': dataframe}


Source.describe(AWSInstancePerformance)
