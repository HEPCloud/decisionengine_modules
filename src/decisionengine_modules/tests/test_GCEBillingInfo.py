# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas
import structlog

from bill_calculator_hep.GCEBillAnalysis import GCEBillCalculator

from decisionengine_modules.GCE.sources import GCEBillingInfo

# TODO
# The GCEBillingInfo module needs to be refactored so that tests
# can be written.  Then tests can be written to test smaller bits
# of code.  There is also an issue that the env has to have
# BOTO_CONFIG set, this has to be done outside of the code and
# can't be set in the test. Depending on how this testing is done
# you may be able to mock around this.

config_billing_info = {
    "channel_name": "Test",
    "projectId": "hepcloud-fnal",
    "lastKnownBillDate": "10/01/18 00:00",  # '%m/%d/%y %H:%M'
    "balanceAtDate": 100.0,  # $
    "accountName": "None",
    "accountNumber": 1111,
    "credentialsProfileName": "BillingBlah",
    "applyDiscount": True,  # DLT discount does not apply to credits
    "botoConfig": ".boto3",
    "localFileDir": ".",
}


class TestGCEBillingInfo:
    def test_produces(self):
        bi_pub = GCEBillingInfo.GCEBillingInfo(config_billing_info)
        assert bi_pub._produces == {"GCE_Billing_Info": pandas.DataFrame}

    def test_unable_to_download_filelist(self):
        constantsDict = {
            "projectId": "hepcloud-fnal",
            "credentialsProfileName": "BillingBlah",
            "accountNumber": 1111,
            "bucketBillingName": "billing-hepcloud-fnal",
            "lastKnownBillDate": "10/01/18 00:00",
            "balanceAtDate": 100.0,
            "applyDiscount": True,
        }
        globalConf = {"graphite_host": "dummy", "graphite_context_billing": "dummy", "outputPath": "."}

        calculator = GCEBillCalculator(None, globalConf, constantsDict, structlog.getLogger())

        file_list = calculator._downloadBillFiles()
        assert file_list == []
