import datetime
import time

import pandas as pd

from bill_calculator_hep.AWSBillAnalysis import AWSBillCalculator

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.AWS.sources import DEAccountContants


@Source.supports_config(
    Parameter(
        "billing_configuration",
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
  }""",
    ),
    Parameter("dst_dir_for_s3_files", type=str, comment="Directory for AWS billing files"),
    Parameter("verbose_flag", type=bool),
)
@Source.produces(AWS_Billing_Info=pd.DataFrame, AWS_Billing_Rate=pd.DataFrame)
class BillingInfo(Source.Source):
    def __init__(self, config):
        super().__init__(config)
        acconts_config_file = config["billing_configuration"]
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )
        self.billing_files_location = config["dst_dir_for_s3_files"]
        self.verbose_flag = int(config["verbose_flag"])
        # Load kown accounts configuration
        account_dict = DEAccountContants.load_constants(acconts_config_file)
        self.accounts = []
        for val in account_dict.values():
            self.accounts.append(DEAccountContants.AccountConstants(val))

    def acquire(self):
        """
        Method to be called from Task Manager.
        redefines acquire from Source.py
        Acquire AWS billing info and return as pandas frame

        :rtype: :obj:`~pd.DataFrame`
        """

        # get data for all accounts
        self.logger.debug("in BillingInfo acquire")
        data = []
        datarate = []
        globalConf = {
            "graphite_host": "dummy",
            "graphite_context_billing": "dummy",
            "outputPath": self.billing_files_location,
            "accountDirs": 1,
        }
        for i in self.accounts:
            constantsDict = {
                "credentialsProfileName": i.credentialsProfileName,
                "accountNumber": i.accountNumber,
                "bucketBillingName": i.bucketBillingName,
                "lastKnownBillDate": i.lastKnownBillDate,
                "balanceAtDate": i.balanceAtDate,
                "applyDiscount": i.applyDiscount,
            }
            try:
                calculator = AWSBillCalculator(i.accountName, globalConf, constantsDict, self.logger)
                lastStartDateBilledConsideredDatetime, CorrectedBillSummaryDict = calculator.CalculateBill()
                self.logger.debug(f"lastStartDateBilledConsideredDatetime: {lastStartDateBilledConsideredDatetime}")
                self.logger.debug(f"CorrectedBillSummaryDict: {CorrectedBillSummaryDict}")
                # data is a list, CorrectedBillSummaryDict is a dict, so we have to append it as a list of dict.
                # data += calculator.CorrectedMonthlyBillSummaryList
                data += [CorrectedBillSummaryDict]
                #
                # This is the code to calculate 6hr and 24hr spend rate
                dateNow = datetime.datetime.today()
                # Get cost in the last 6 hours
                sixHoursBeforeLastDateBilledDatetime = lastStartDateBilledConsideredDatetime - datetime.timedelta(
                    hours=6
                )
                calculator.setLastKnownBillDate(sixHoursBeforeLastDateBilledDatetime.strftime("%m/%d/%y %H:%M"))
                newLastStartDateBilledDatetime, CorrectedBillSummarySixHoursBeforeDict = calculator.CalculateBill()
                costInLastSixHours = CorrectedBillSummarySixHoursBeforeDict["Total"]
                costRatePerHourInLastSixHours = costInLastSixHours / 6
                # Get cost in the last 24 hours
                oneDayBeforeLastDateBilledDatetime = lastStartDateBilledConsideredDatetime - datetime.timedelta(
                    hours=24
                )
                calculator.setLastKnownBillDate(oneDayBeforeLastDateBilledDatetime.strftime("%m/%d/%y %H:%M"))
                newLastStartDateBilledDatetime, CorrectedBillSummaryOneDayBeforeDict = calculator.CalculateBill()

                costInLastDay = CorrectedBillSummaryOneDayBeforeDict["Total"]
                costRatePerHourInLastDay = costInLastDay / 24
                dataDelay = int(
                    (time.mktime(dateNow.timetuple()) - time.mktime(lastStartDateBilledConsideredDatetime.timetuple()))
                    / 3600
                )

                dataratedict = {
                    "accountName": i.accountName,
                    "lastStartDateBilledConsideredDatetime": lastStartDateBilledConsideredDatetime,
                    "dataDelay": dataDelay,
                    "costInLastSixHours": costInLastSixHours,
                    "costInLastDay": costInLastDay,
                    "costRatePerHourInLastSixHours": costRatePerHourInLastSixHours,
                    "costRatePerHourInLastDay": costRatePerHourInLastDay,
                }
                datarate += [dataratedict]
                if self.verbose_flag:
                    self.logger.debug("---")
                    self.logger.debug(
                        f"Alarm Computation for {calculator.accountName} Account Finished at {time.strftime('%c')}"
                    )
                    self.logger.debug("")
                    self.logger.debug(
                        f"Last Start Date Billed Considered: {lastStartDateBilledConsideredDatetime.strftime('%m/%d/%y %H:%M')}"
                    )
                    self.logger.debug(f"Now {dateNow.strftime('%m/%d/%y %H:%M')}")
                    self.logger.debug(f"delay between now and Last Start Date Billed Considered in hours {dataDelay}")
                    self.logger.debug(
                        f"Six hours before that: {sixHoursBeforeLastDateBilledDatetime.strftime('%m/%d/%y %H:%M')}"
                    )
                    self.logger.debug(
                        f"One day before that: {oneDayBeforeLastDateBilledDatetime.strftime('%m/%d/%y %H:%M')}"
                    )
                    self.logger.debug(
                        f"Adjusted Total Now from Date of Last Known Balance: ${CorrectedBillSummaryDict['Total']}"
                    )
                    self.logger.debug("")
                    self.logger.debug(f"Cost In the Last Six Hours: ${costInLastSixHours}")
                    self.logger.debug(f"Cost Rate Per Hour In the Last Six Hours: ${costRatePerHourInLastSixHours} / h")
                    self.logger.debug("")
                    self.logger.debug(f"Cost In the Last Day: ${costInLastDay}")
                    self.logger.debug(f"Cost Rate Per Hour In the Last Day: ${costRatePerHourInLastDay} / h")
                    self.logger.debug("---")
                    self.logger.debug("")

            except Exception as detail:
                self.logger.exception("Exception in AWS BillingInfo call to acquire")
                raise Exception(detail)

        return {"AWS_Billing_Info": pd.DataFrame(data), "AWS_Billing_Rate": pd.DataFrame(datarate)}


Source.describe(
    BillingInfo,
    sample_config={
        "billing_configuration": "/etc/decisionengine/modules.conf/AccountConstants_my.py",
        "dst_dir_for_s3_files": "/var/lib/decisionengine/awsfiles",
    },
)
