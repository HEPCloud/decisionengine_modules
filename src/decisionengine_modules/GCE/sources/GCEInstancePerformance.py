"""
This source takes input from instance_performance_gce.csv
and adds it to data block
"""
import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter


@Source.supports_config(Parameter("csv_file", type=str, comment="path to CSV file"))
@Source.produces(GCE_Instance_Performance=pd.DataFrame)
class GCEInstancePerformance(Source.Source):
    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )
        self.csv_file = config.get("csv_file")
        if not self.csv_file:
            raise RuntimeError("No csv file found in configuration")

    def acquire(self):
        self.logger.debug("in GCEInstancePerformance acquire")
        return {"GCE_Instance_Performance": pd.read_csv(self.csv_file)}


Source.describe(GCEInstancePerformance)
