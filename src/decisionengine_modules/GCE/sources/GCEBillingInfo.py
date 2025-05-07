# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

# standard library imports
import pandas as pd

# related third party imports
from bill_calculator_hep.GCEBillAnalysis import GCEBillCalculator

# local application/library specific imports
from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter


@Source.supports_config(
    Parameter("projectId", type=str),
    Parameter("lastKnownBillDate", type=str, comment="in the form '%m/%d/%y %H:%M'"),
    Parameter("balanceAtDate", type=float, comment="in dollars"),
    Parameter("applyDiscount", type=bool, comment="DLT discount does not apply to credits"),
    Parameter("sumToDate", type=str, comment="in the form '%m/%d/%y %H:%M'"),
)
@Source.produces(GCE_Billing_Info=pd.DataFrame)
class GCEBillingInfo(Source.Source):
    def __init__(self, config):
        super().__init__(config)
        # Load configuration "constants"
        self.projectId = config.get("projectId")
        self.lastKnownBillDate = config.get("lastKnownBillDate")  # '%m/%d/%y %H:%M'
        self.balanceAtDate = config.get("balanceAtDate")  # $
        # Onix does not provide discounts
        self.applyDiscount = config.get("applyDiscount")
        self.sumToDate = config.get("sumToDate")

    def acquire(self):
        """
        Acquire GCE billing info and return as pandas frame

        :rtype: :obj:`~pd.DataFrame`
        """
        self.logger.debug("in GCEBillingInfo acquire")
        constantsDict = {
            "projectId": self.projectId,
            "lastKnownBillDate": self.lastKnownBillDate,
            "balanceAtDate": self.balanceAtDate,
            "applyDiscount": self.applyDiscount,
            "sumToDate": self.sumToDate,
        }
        globalConf = {"graphite_host": "dummy", "graphite_context_billing": "dummy"}
        bill_summary = pd.DataFrame()
        try:
            calculator = GCEBillCalculator(None, globalConf, constantsDict, self.logger)

            bill_summary = calculator.calculate_bill()

            self.logger.info("Calculated corrected bill summary for Google (using BigQuery)")
            self.logger.debug(bill_summary)

        except Exception:
            self.logger.exception("Exception in GCEBillingInfo call to acquire")

        return {"GCE_Billing_Info": bill_summary}


Source.describe(GCEBillingInfo)
