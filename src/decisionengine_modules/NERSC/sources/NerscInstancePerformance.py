"""
This source takes input from instance_performance_nersc.csv
and adds it to data block
"""
import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter

@Source.supports_config(Parameter('csv_file', type=str, comment="path to CSV file"))
@Source.produces(Nersc_Instance_Performance=pd.DataFrame)
class NerscInstancePerformance(Source.Source):

    def __init__(self, config):
        super().__init__(config)
        self.csv_file = config.get('csv_file')
        if not self.csv_file:
            raise RuntimeError("No csv file found in configuration")
        self.logger = self.logger.bind(module=__name__.split(".")[-1])

    def acquire(self):
        self.get_logger().debug("in NerscInstancePerformance::acquire()")
        return {'Nersc_Instance_Performance': pd.read_csv(self.csv_file)}


Source.describe(NerscInstancePerformance)
