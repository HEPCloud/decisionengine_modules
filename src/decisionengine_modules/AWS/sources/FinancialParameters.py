import pandas

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter

_SAMPLE_CONFIG = {
    "target_aws_vm_burn_rate": [9.0],
    "target_aws_bill_burn_rate": [10.0],
    "target_aws_balance": [1000.0],
    "target_gce_vm_burn_rate": [9.0],
    "target_gce_balance": [1000.0],
}


@Source.supports_config(
    Parameter("financial_parameters", default=_SAMPLE_CONFIG, comment="specifies the desired burn rates and balances")
)
@Source.produces(financial_params=pandas.DataFrame)
class FinancialParameters(Source.Source):
    def __init__(self, config):
        super().__init__(config)
        self.financial_parameters_dict = config.get("financial_parameters")
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )

    # The DataBlock given to the source is t=0
    def acquire(self):
        """
        Read the financial parameters from the config file and
        return as a dataframe
        """
        self.logger.debug("in FinancialParameters acquire")
        return {"financial_params": pandas.DataFrame(self.financial_parameters_dict)}


Source.describe(FinancialParameters, sample_config=_SAMPLE_CONFIG)
