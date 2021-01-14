import datetime
import logging
import os
import pprint
import time
import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine_modules.AWS.sources import DEAccountContants
from bill_calculator_hep.AWSBillAnalysis import AWSBillCalculator
PRODUCES = ['AWS_Billing_Info', 'AWS_Billing_Rate']

class BillingInfo(Source.Source):
    def __init__(self, *args, **kwargs):
        acconts_config_file = args[0]['billing_configuration']
        self.logger = logging.getLogger()
        self.billing_files_location = args[0]['dst_dir_for_s3_files']
        self.verbose_flag = int(args[0]['verbose_flag'])
        # Load kown accounts configuration
        account_dict = DEAccountContants.load_constants(acconts_config_file)
        self.accounts = []
        for k, val in account_dict.items():
            self.accounts.append(DEAccountContants.AccountConstants(val))

    def produces(self, schema_id_list):
        """
        Method to be called from Task Manager.
        Copied from Source.py
        Do not know why schema_id_list is needed here.
        """

        return PRODUCES

    def acquire(self):
        """
        Method to be called from Task Manager.
        redefines acquire from Source.py
        Acquire AWS billing info and return as pandas frame

        :rtype: :obj:`~pd.DataFrame`
        """

        # get data for all accounts
        data = []
        datarate = []
        globalConf = {'graphite_host': 'dummy', 'graphite_context_billing': 'dummy', 'outputPath': self.billing_files_location, 'accountDirs': 1}
        for i in self.accounts:
            constantsDict = {'credentialsProfileName': i.credentialsProfileName, 'accountNumber': i.accountNumber,
                             'bucketBillingName': i.bucketBillingName, 'lastKnownBillDate': i.lastKnownBillDate,
                             'balanceAtDate': i.balanceAtDate, 'applyDiscount': i.applyDiscount}
            try:
                calculator = AWSBillCalculator(i.accountName, globalConf, constantsDict, self.logger)
                lastStartDateBilledConsideredDatetime, CorrectedBillSummaryDict = calculator.CalculateBill()
                self.logger.debug('lastStartDateBilledConsideredDatetime: %s' % (
                    lastStartDateBilledConsideredDatetime))
                self.logger.debug('CorrectedBillSummaryDict: %s' %
                                  (CorrectedBillSummaryDict))
                # data is a list, CorrectedBillSummaryDict is a dict, so we have to append it as a list of dict.
                # data += calculator.CorrectedMonthlyBillSummaryList
                data += [CorrectedBillSummaryDict]
                #
                # This is the code to calculate 6hr and 24hr spend rate
                dateNow = datetime.datetime.today()
                # Get cost in the last 6 hours
                sixHoursBeforeLastDateBilledDatetime = lastStartDateBilledConsideredDatetime - datetime.timedelta(
                    hours=6)
                calculator.setLastKnownBillDate(
                    sixHoursBeforeLastDateBilledDatetime.strftime('%m/%d/%y %H:%M'))
                newLastStartDateBilledDatetime, CorrectedBillSummarySixHoursBeforeDict = calculator.CalculateBill()
                costInLastSixHours = CorrectedBillSummarySixHoursBeforeDict['Total']
                costRatePerHourInLastSixHours = costInLastSixHours / 6
                # Get cost in the last 24 hours
                oneDayBeforeLastDateBilledDatetime = lastStartDateBilledConsideredDatetime - datetime.timedelta(
                    hours=24)
                calculator.setLastKnownBillDate(
                    oneDayBeforeLastDateBilledDatetime.strftime('%m/%d/%y %H:%M'))
                newLastStartDateBilledDatetime, CorrectedBillSummaryOneDayBeforeDict = calculator.CalculateBill()

                costInLastDay = CorrectedBillSummaryOneDayBeforeDict['Total']
                costRatePerHourInLastDay = costInLastDay / 24
                dataDelay = int((time.mktime(dateNow.timetuple()) - time.mktime(
                    lastStartDateBilledConsideredDatetime.timetuple())) / 3600)

                dataratedict = {'accountName': i.accountName,
                                'lastStartDateBilledConsideredDatetime': lastStartDateBilledConsideredDatetime,
                                'dataDelay': dataDelay, 'costInLastSixHours': costInLastSixHours,
                                'costInLastDay': costInLastDay,
                                'costRatePerHourInLastSixHours': costRatePerHourInLastSixHours,
                                'costRatePerHourInLastDay': costRatePerHourInLastDay}
                datarate += [dataratedict]
                if self.verbose_flag:
                    self.logger.debug('---')
                    self.logger.debug('Alarm Computation for %s Account Finished at %s' % (
                        calculator.accountName, time.strftime("%c")))
                    self.logger.debug('')
                    self.logger.debug(
                        'Last Start Date Billed Considered: {}'.format(lastStartDateBilledConsideredDatetime.strftime(
                            '%m/%d/%y %H:%M')))
                    self.logger.debug(
                        'Now {}'.format(dateNow.strftime('%m/%d/%y %H:%M')))
                    self.logger.debug(
                        'delay between now and Last Start Date Billed Considered in hours {}'.format(dataDelay))
                    self.logger.debug(
                        'Six hours before that: {}'.format(sixHoursBeforeLastDateBilledDatetime.strftime('%m/%d/%y %H:%M')))
                    self.logger.debug(
                        'One day before that: {}'.format(oneDayBeforeLastDateBilledDatetime.strftime('%m/%d/%y %H:%M')))
                    self.logger.debug('Adjusted Total Now from Date of Last Known Balance: ${}'.format(
                                      CorrectedBillSummaryDict['Total']))
                    self.logger.debug('')
                    self.logger.debug(
                        'Cost In the Last Six Hours: ${}'.format(costInLastSixHours))
                    self.logger.debug('Cost Rate Per Hour In the Last Six Hours: ${} / h'.format(costRatePerHourInLastSixHours))
                    self.logger.debug('')
                    self.logger.debug('Cost In the Last Day: ${}'.format(costInLastDay))
                    self.logger.debug(
                        'Cost Rate Per Hour In the Last Day: ${} / h'.format(costRatePerHourInLastDay))
                    self.logger.debug('---')
                    self.logger.debug('')

            except Exception as detail:
                self.logger.error("In acquire: %s" % detail)
                raise Exception(detail)

        return {PRODUCES[0]: pd.DataFrame(data), PRODUCES[1]: pd.DataFrame(datarate)}


def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"BillingInfo": {
        "module": "modules.AWS.sources.BillingInfo",
        "name": "BillingInfo",
        "parameters": {
            "billing_configuration": "%s/de_config/AccountConstants_my.py" % (os.environ.get('HOME'),),
            "dst_dir_for_s3_files": "%s/de_tmp_aws_files" % (os.environ.get('HOME'),),
        },
        "schedule": 6 * 60 * 60,
    }
    }
    account_info = {'AWSRnDAccountConstants':
                    {
                        'lastKnownBillDate': '08/01/16 00:00',  # '%m/%d/%y %H:%M'
                        'balanceAtDate': 3839.16,  # $
                        'accountName': 'RnD',
                        'accountNumber': 159067897602,
                        'credentialsProfileName': 'BillingRnD',
                        'applyDiscount': True,  # DLT discount does not apply to credits
                        'costRatePerHourInLastSixHoursAlarmThreshold': 2,  # $ / h # $10/h
                        'costRatePerHourInLastDayAlarmThreshold': 2,  # $ / h # $10/h
                        'emailReceipientForAlarms': 'fermilab-cloud-facility-rnd@fnal.gov'
                    }
                    }

    print("Entry in channel configuration")
    pprint.pprint(d)
    print("where")
    print("\t name - name of the class to be instantiated by task manager")
    print("\t billing_configuration - configuration requred to get AWS billing information")
    print("\t Example of Billing configuration file:")
    print("-------------")
    pprint.pprint(account_info)
    print("-------------")
    print("\t dst_dir_for_s3_files - directory for AWS billing files")
    print("\t schedule - execution period")


def module_config_info():
    """
    print this module configuration information
    """
    print("produces", PRODUCES)
    module_config_template()


def main():
    """
    Call this a a test unit or use as CLI of this module
    """
    import argparse
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
        bi = BillingInfo({'billing_configuration': '/etc/decisionengine/modules.conf/AccountConstants_my.py',
                          'dst_dir_for_s3_files': '/var/lib/decisionengine/awsfiles'})
        rc = bi.acquire()
        print("INFO")
        print(rc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
