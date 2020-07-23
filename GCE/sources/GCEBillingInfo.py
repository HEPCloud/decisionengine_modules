import argparse
import csv
import datetime
import gcs_oauth2_boto_plugin
import io
import json
import logging
import os
import pprint
import re
import time

import boto
import pandas as pd
from boto.exception import NoAuthHandlerFound

from decisionengine.framework.modules import Source
from GCEBillAnalysis import GCEBillCalculator

PRODUCES = ['GCE_Billing_Info']

class GCEBillingInfo(Source.Source):

    def __init__(self, config):
        super(GCEBillingInfo, self).__init__(config)
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

        self.logger = logging.getLogger()

    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES

    def acquire(self):
        """
        Acquire GCE billing info and return as pandas frame

        :rtype: :obj:`~pd.DataFrame`
        """
        constantsDict = {'projectId': self.projectId, 'credentialsProfileName': self.credentialsProfileName, 'accountNumber': self.accountNumber,\
                         'bucketBillingName': 'billing-' + str(self.projectId),'lastKnownBillDate': self.lastKnownBillDate, \
                         'balanceAtDate': self.balanceAtDate, 'applyDiscount': self.applyDiscount}
        globalConf = {'graphite_host':'dummy', 'graphite_context_billing': 'dummy', 'outputPath': self.localFileDir}
        try:
            calculator = GCEBillCalculator( None, globalConf, constantsDict, self.logger )

            lastStartDateBilledConsideredDatetime, CorrectedBillSummaryDict = calculator.CalculateBill()

            self.logger.info('Calculated corrected bill summary for google')
            self.logger.info(CorrectedBillSummaryDict)

        except Exception as detail:
            self.logger.error(detail)

        return {PRODUCES[0]: pd.DataFrame([CorrectedBillSummaryDict])}


def module_config_template():
    """
    print a template for this module configuration data
    """

    template = {
        "GCEBillingInfo": {
            "module": "modules.GCE.sources.GCEBillingInfo",
            "name": "GCEBillingInfo",
            "parameters": {
                'projectId': 'Blah',
                'lastKnownBillDate': '01/01/18 00:00',  # '%m/%d/%y %H:%M'
                'balanceAtDate': 100.0,    # $
                'accountName': 'Blah',
                'accountNumber': 1111,
                'credentialsProfileName': 'BillingBlah',
                'applyDiscount': True,  # DLT discount does not apply to credits
                'botoConfig': "path_to_file",
                'locaFileDir': "dir_for_billing_files"
            },
            "schedule": 24 * 60 * 60,
        }
    }

    print("GCE Billing Info")
    pprint.pprint(template)


def module_config_info():
    """
    print this module configuration information
    """
    print("produces", PRODUCES)
    module_config_template()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--configtemplate',
                        action='store_true',
                        help='prints the expected module configuration')

    parser.add_argument('--configinfo',
                        action='store_true',
                        help='prints config template along with produces and consumes info')
    args = parser.parse_args()
    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == "__main__":
    main()
