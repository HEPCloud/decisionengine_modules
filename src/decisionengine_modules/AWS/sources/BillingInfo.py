import datetime
import time
import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.AWS.sources import DEAccountContants
from bill_calculator_hep.AWSBillAnalysis import AWSBillCalculator


@Source.supports_config(Parameter('billing_configuration',
                                  type=dict,
                                  comment="""Configuration required to get AWS billing information.  Supports the layout:

  {
    'AWSRnDAccountConstants': {
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
  }"""),
                        Parameter('dst_dir_for_s3_files', type=str, comment="Directory for AWS billing files"),
                        Parameter('verbose_flag', type=bool))
@Source.produces(AWS_Billing_Info=pd.DataFrame,
                 AWS_Billing_Rate=pd.DataFrame)
class BillingInfo(Source.Source):
    def __init__(self, config):
        super().__init__(config)
        acconts_config_file = config['billing_configuration']
        self.logger = self.logger.bind(module=__name__.split(".")[-1])
        self.billing_files_location = config['dst_dir_for_s3_files']
        self.verbose_flag = int(config['verbose_flag'])
        # Load kown accounts configuration
        account_dict = DEAccountContants.load_constants(acconts_config_file)
        self.accounts = []
        for k, val in account_dict.items():
            self.accounts.append(DEAccountContants.AccountConstants(val))

    def acquire(self):
        """
        Method to be called from Task Manager.
        redefines acquire from Source.py
        Acquire AWS billing info and return as pandas frame

        :rtype: :obj:`~pd.DataFrame`
        """

        self.get_logger().debug("in BillingInfo::acquire()")
        # get data for all accounts
        data = []
        datarate = []
        globalConf = {'graphite_host': 'dummy', 'graphite_context_billing': 'dummy', 'outputPath': self.billing_files_location, 'accountDirs': 1}
        for i in self.accounts:
            constantsDict = {'credentialsProfileName': i.credentialsProfileName, 'accountNumber': i.accountNumber,
                             'bucketBillingName': i.bucketBillingName, 'lastKnownBillDate': i.lastKnownBillDate,
                             'balanceAtDate': i.balanceAtDate, 'applyDiscount': i.applyDiscount}
            try:
                calculator = AWSBillCalculator(i.accountName, globalConf, constantsDict, self.get_logger())
                lastStartDateBilledConsideredDatetime, CorrectedBillSummaryDict = calculator.CalculateBill()
                self.get_logger().debug('lastStartDateBilledConsideredDatetime: %s' % (
                    lastStartDateBilledConsideredDatetime))
                self.get_logger().debug('CorrectedBillSummaryDict: %s' %
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
                    self.get_logger().debug('---')
                    self.get_logger().debug('Alarm Computation for %s Account Finished at %s' % (
                        calculator.accountName, time.strftime("%c")))
                    self.get_logger().debug('')
                    self.get_logger().debug(
                        'Last Start Date Billed Considered: {}'.format(lastStartDateBilledConsideredDatetime.strftime(
                            '%m/%d/%y %H:%M')))
                    self.get_logger().debug(
                        'Now {}'.format(dateNow.strftime('%m/%d/%y %H:%M')))
                    self.get_logger().debug(
                        'delay between now and Last Start Date Billed Considered in hours {}'.format(dataDelay))
                    self.get_logger().debug(
                        'Six hours before that: {}'.format(sixHoursBeforeLastDateBilledDatetime.strftime('%m/%d/%y %H:%M')))
                    self.get_logger().debug(
                        'One day before that: {}'.format(oneDayBeforeLastDateBilledDatetime.strftime('%m/%d/%y %H:%M')))
                    self.get_logger().debug('Adjusted Total Now from Date of Last Known Balance: ${}'.format(
                                            CorrectedBillSummaryDict['Total']))
                    self.get_logger().debug('')
                    self.get_logger().debug(
                        'Cost In the Last Six Hours: ${}'.format(costInLastSixHours))
                    self.get_logger().debug('Cost Rate Per Hour In the Last Six Hours: ${} / h'.format(costRatePerHourInLastSixHours))
                    self.get_logger().debug('')
                    self.get_logger().debug('Cost In the Last Day: ${}'.format(costInLastDay))
                    self.get_logger().debug(
                        'Cost Rate Per Hour In the Last Day: ${} / h'.format(costRatePerHourInLastDay))
                    self.get_logger().debug('---')
                    self.get_logger().debug('')

            except Exception as detail:
                self.get_logger().exception("Exception in AWS BillingInfo call to acquire")
                raise Exception(detail)

        return {'AWS_Billing_Info': pd.DataFrame(data),
                'AWS_Billing_Rate': pd.DataFrame(datarate)}


Source.describe(BillingInfo,
                sample_config={'billing_configuration': '/etc/decisionengine/modules.conf/AccountConstants_my.py',
                               'dst_dir_for_s3_files': '/var/lib/decisionengine/awsfiles'})
