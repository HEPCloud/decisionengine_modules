import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from bill_calculator_hep.GCEBillAnalysis import GCEBillCalculator


@Source.supports_config(Parameter('projectId', type=str),
                        Parameter('credentialsProfileName', type=str, comment="not currently used"),
                        Parameter('accountNumber', type=int, comment="not currently used"),
                        Parameter('lastKnownBillDate', type=str, comment="in the form '%m/%d/%y %H:%M'"),
                        Parameter('balanceAtData', type=float, comment="in dollars"),
                        Parameter('applyDiscount', type=bool, comment="DLT discount does not apply to credits"),
                        Parameter('botoConfig', comment="not currently used"),
                        Parameter('localFileDir', type=dir, comment="location for downloaded billing files"))
@Source.produces(GCE_Billing_Info=pd.DataFrame)
class GCEBillingInfo(Source.Source):

    def __init__(self, config):
        super().__init__(config)
        # Load configuration "constants"
        self.projectId = config.get('projectId')
        self.credentialsProfileName = config.get(
            'credentialsProfileName')  # NOT CURRENTLY USED
        self.accountNumber = config.get('accountNumber')  # NOT CURRENTLY USED
        self.lastKnownBillDate = config.get(
            'lastKnownBillDate')  # '%m/%d/%y %H:%M'
        self.balanceAtDate = config.get('balanceAtDate')  # $
        # Onix does not provide discounts
        self.applyDiscount = config.get('applyDiscount')
        self.botoConfig = config.get('botoConfig')  # BOTO_CONFIG env
        # location for downloaded billing files
        self.localFileDir = config.get('localFileDir')
        self.logger = self.logger.bind(module=__name__.split(".")[-1])

    def acquire(self):
        """
        Acquire GCE billing info and return as pandas frame

        :rtype: :obj:`~pd.DataFrame`
        """
        self.get_logger().debug("in GCEBillingInfo::acquire()")
        constantsDict = {'projectId': self.projectId, 'credentialsProfileName': self.credentialsProfileName, 'accountNumber': self.accountNumber,
                         'bucketBillingName': 'billing-' + str(self.projectId), 'lastKnownBillDate': self.lastKnownBillDate,
                         'balanceAtDate': self.balanceAtDate, 'applyDiscount': self.applyDiscount}
        globalConf = {'graphite_host': 'dummy', 'graphite_context_billing': 'dummy', 'outputPath': self.localFileDir}
        try:
            calculator = GCEBillCalculator(None, globalConf, constantsDict, self.logger)

            lastStartDateBilledConsideredDatetime, CorrectedBillSummaryDict = calculator.CalculateBill()

            self.get_logger().info('Calculated corrected bill summary for google')
            self.get_logger().info(CorrectedBillSummaryDict)

        except Exception:
            self.get_logger().exception("Exception in GCEBillingInfo call to acquire")

        return {'GCE_Billing_Info': pd.DataFrame([CorrectedBillSummaryDict])}


Source.describe(GCEBillingInfo)
