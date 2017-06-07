#!/usr/bin/env python
import boto3
from boto3.session import Session
import zipfile
import csv, StringIO
import string, re
import datetime, time
import sys
import os
import copy
import numpy as np
import pandas as pd

from decisionengine.framework.modules import Source
import DEAccountContants
import pprint

PRODUCES = ['AWS_Billing_Info']

class AWSBillCalculator(object):
    """
    Calculate AWS bill
    """

    def __init__(self, accountName, accountProfileName, accountNumber, lastKnownBillDate, balanceAtDate, applyDiscount, sumToDate = None, tmpDirForBuillingFiles = '.', verboseFlag = True, debugFlag = False):
        # Configuration parameters
        self.accountName = accountName
        self.accountProfileName = accountProfileName
        self.accountNumber = accountNumber
        self.bucketBillingName = str(accountNumber) + '-dlt-utilization'
        # Expect lastKnownBillDate as '%m/%d/%y %H:%M' : validated when needed
        self.lastKnownBillDate = lastKnownBillDate
        self.balanceAtDate = balanceAtDate # $
        self.applyDiscount = applyDiscount
        self.sumToDate = sumToDate
        self.verboseFlag = verboseFlag
        self.debugFlag = debugFlag
        self.tmpDirForBuillingFiles = os.path.join(tmpDirForBuillingFiles, self.accountName)
        self.CorrectedBillSummaryDict= {
            'AccountName': self.accountName,
            'AWSCloudTrail': 0.,
            'AWSConfig': 0.,
            'AWSKeyManagementService': 0.0,
            'AWSLambda': 0.0,
            'AWSSupportBusiness': 0.,
            'AdjustedSupport': 0.,
            'AdjustedTotal': 0.,
            'AmazonCloudWatch': 0.0,
            'AmazonElasticComputeCloud': 0.0,
            'AmazonRoute53': 0.0,
            'AmazonSimpleNotificationService': 0.0,
            'AmazonSimpleQueueService': 0.0,
            'AmazonSimpleStorageService': 0.0,
            'Balance': 0.0,
            'EstimatedTotalDataOut': 0.0,
            'Total': 0.0,
            'TotalDataOut': 0.0
        }
        #self.MonthlyBillSummaryList = []
        self.CorrectedMonthlyBillSummaryList = []

        # Can save state for repetitive calls e.g. for alarms
        self.billCVSAggregateStr = None

        boto3.setup_default_session(profile_name=accountProfileName)

    def setLastKnownBillDate(self, lastKnownBillDate):
        self.lastKnownBillDate = lastKnownBillDate

    def setBalanceAtDate(self, balanceAtDate):
        self.balanceAtDate = balanceAtDate

    def setSumToDate(self, sumToDate):
        self.sumToDate = sumToDate

    def CalculateBill(self):
        """
        Select and download the billing file from S3; aggregate them.
        Calculates sum and corrects for discounts, data egress waiver,
        etc.

        :rtype: :obj:`dict`

        Returns::

            ( lastStartDateBilledConsideredDatetime, BillSummaryDict )
                Example BillSummaryDict:
                 {'AdjustedSupport': 24.450104610658975, 'AWSKeyManagementService': 0.0,
                  'AmazonRoute53': 7.42, 'AmazonSimpleNotificationService': 0.0,
                  'AmazonElasticComputeCloud': 236.5393058537243,
                  'AmazonSimpleQueueService': 0.0, 'TotalDataOut': 0.0,
                  'AmazonSimpleStorageService': 0.15311901797500035,
                  'Balance': 299731.0488492827, 'Total': 244.50104610658974,
                  'AWSSupportBusiness': 0.38862123489039674,
                  'AdjustedTotal': 268.9511507172487
                 }
        """

        # Load data in memory
        if self.billCVSAggregateStr == None:
            fileNameForDownloadList = self._downloadBillFiles()
            cwd = os.getcwd()
            os.chdir(self.tmpDirForBuillingFiles)
            self.data_by_month = self._billingDataByMonth(fileNameForDownloadList)
            os.chdir(cwd)
        self.billCVSAggregateStr = self._aggregateBillFiles(self.data_by_month)

        keylist = self.data_by_month.keys()
        keylist.sort()
        for k in keylist:
            dt =datetime.datetime(int(k.split('-')[0]), int(k.split('-')[1]), 1)
            dt_s = dt.strftime('%m/%d/%y %H:%M')
            lastStartMontlyDateBilledConsideredDatetime, MonthlyBillSummary = self._sumUpBillFromDateToDate( self.data_by_month[k], dt_s);
            CorrectedMonthlyBillSummary = self._applyBillCorrections(MonthlyBillSummary);
            CorrectedMonthlyBillSummary['Date'] = k
            self.CorrectedMonthlyBillSummaryList.append(copy.copy(CorrectedMonthlyBillSummary))

        lastStartDateBilledConsideredDatetime, BillSummaryDict = self._sumUpBillFromDateToDate( self.billCVSAggregateStr, self.lastKnownBillDate, self.sumToDate );

        CorrectedBillSummaryDict = self._applyBillCorrections(BillSummaryDict);

        if self.verboseFlag:
            print '---'
            print 'Bill Computation for %s Account Finished at %s' % ( self.accountName, time.strftime("%c") )
            print
            print 'Last Start Date Billed Considered : ' + lastStartDateBilledConsideredDatetime.strftime('%m/%d/%y %H:%M')
            print 'Last Known Balance :' + str(self.balanceAtDate)
            print
            print 'BillSummaryDict:'
            print BillSummaryDict
            print
            print 'CorrectedBillSummaryDict'
            print CorrectedBillSummaryDict
        if self.debugFlag:
            print '---'
            print 'Bill Computation for %s Account Finished at %s' % ( self.accountName, time.strftime("%c") )
            print
            print 'Last Start Date Billed Considered : ' + lastStartDateBilledConsideredDatetime.strftime('%m/%d/%y %H:%M')
            print 'Last Known Balance :' + str(self.balanceAtDate)
            print
            print 'BillSummaryDict:'
            print BillSummaryDict
            print
            print 'CorrectedBillSummaryDict'
            print CorrectedBillSummaryDict


        return lastStartDateBilledConsideredDatetime, CorrectedBillSummaryDict

    '''
    Leave this just as a example
    def sendDataToGraphite(self, CorrectedBillSummaryDict ):
        """Send the corrected bill summary dictionary to the Graphana dashboard for the
        bill information
        Args:
            CorrectedBillSummaryDict: the billing data to send Graphite.
                 Example dict:
                 {'AdjustedSupport': 24.450104610658975, 'AWSKeyManagementService': 0.0,
                  'AmazonRoute53': 7.42, 'AmazonSimpleNotificationService': 0.0,
                  'AmazonElasticComputeCloud': 236.5393058537243,
                  'AmazonSimpleQueueService': 0.0, 'TotalDataOut': 0.0,
                  'AmazonSimpleStorageService': 0.15311901797500035,
                  'Balance': 299731.0488492827, 'Total': 244.50104610658974,
                  'AWSSupportBusiness': 0.38862123489039674,
                  'AdjustedTotal': 268.9511507172487
                 }

        Returns:
            none
        """

        #Constants
        # Data available from http://fermicloud399.fnal.gov:8080/ and http://fermicloud399.fnal.gov/hcf-priv/
        graphiteHostString='fermicloud399.fnal.gov'
        graphiteContextString='hepcloud_priv.aws_balance.' + str(self.accountName)
        #graphiteContextString='test'

        graphiteEndpoint = graphite.Graphite(host=graphiteHostString)
        graphiteEndpoint.send_dict(graphiteContextString, CorrectedBillSummaryDict,  debug_print=True, send_data=True)

    '''

    def _obtainRoleBasedSession(self):
        """
        Obtain a short-lived role-based token

        Prerequisites:

        arn:aws:iam::950490332792:role/CalculateBill is created in our accounts
        with the following Trust relationship::

         {
             "Version": "2012-10-17",
             "Statement": [
                 {
                     "Effect": "Allow",
                     "Principal": {
                         "AWS": "arn:aws:iam::950490332792:user/Billing"
                         },
                     "Action": "sts:AssumeRole"
                     },
                 ]
             }
         }


         and policy BillCalculatorReadAccess as follows:
         {
             "Version": "2012-10-17",
             "Statement": [
                 {
                     "Effect": "Allow",
                     "Action": [
                         "s3:GetObject"
                     ],
                     "Resource": [
                         "arn:aws:s3:::950490332792-dlt-utilization/*"
                     ]
                 },
                 {
                     "Effect": "Allow",
                     "Action": [
                         "s3:ListBucket"
                     ],
                     "Resource": [
                         "arn:aws:s3:::950490332792-dlt-utilization"
                     ]
                 }
             ]
         }

        """

        roleNameString = 'CalculateBill'
        fullRoleNameString = 'arn:aws:iam::' + str(self.accountNumber) + ':role/' + roleNameString

        # using boto3 default session to obtain temporary token
        # long term credentials have ONLY the permission to assume role CalculateBill
        client = boto3.client('sts')
        response = client.assume_role( RoleArn=fullRoleNameString, RoleSessionName='roleSwitchSession'  )
        role_AK_id = response['Credentials']['AccessKeyId']
        role_AK_sc = response['Credentials']['SecretAccessKey']
        role_AK_tk = response['Credentials']['SessionToken']

        if self.verboseFlag:
            print
            print 'Opening Role-based Session for account %s with temporary key for role %s' % (self.accountName, fullRoleNameString)
        session = Session(aws_access_key_id=role_AK_id, aws_secret_access_key=role_AK_sc, aws_session_token=role_AK_tk)
        return session


    def _downloadBillFiles(self ):
        """
        Download AWS billing files

        :rtype: :obj:`list` - list of downloaded files
        """

        #Identify what files need to be downloaded, given the last known balance date
        # Download the files from S3

        session = self._obtainRoleBasedSession()

        s3 = session.client('s3')
        filesObjsInBucketDict = s3.list_objects(Bucket=self.bucketBillingName)
        filesDictList = filesObjsInBucketDict['Contents']
        # Assumption: sort files by date using file name: this is true if file name convention is maintained
        filesDictList.sort(key=lambda filesDict: filesDict['Key'])



        # Extract file creation date from the file name
        # Assume a format such as this: 950490332792-aws-billing-detailed-line-items-2015-09.csv.zip
        billingFileNameIdentifier = 'aws\-billing.*\-20[0-9][0-9]\-[0-9][0-9].csv.zip'
        billingFileMatch = re.compile(billingFileNameIdentifier)
        billingFileDateIdentifier = '20[0-9][0-9]\-[0-9][0-9]'
        dateExtractionMatch = re.compile(billingFileDateIdentifier)
        if self.lastKnownBillDate:
            lastKnownBillDateDatetime = datetime.datetime(*(time.strptime(self.lastKnownBillDate, '%m/%d/%y %H:%M')[0:6]))
        else:
            lastKnownBillDateDatetime = self.lastKnownBillDate

        if self.verboseFlag or self.debugFlag:
             print 'lastKnownBillDate ' +  self.lastKnownBillDate
        fileNameForDownloadList = []
        previousFileForDownloadListDateTime = None
        previousFileNameForDownloadListString = None
        noFileNameMatchesFileNameIdentifier = True
        for filesDict in filesDictList:
           if self.verboseFlag or self.debugFlag:
               print 'File in bucket ' + self.bucketBillingName + ' : ' +  filesDict['Key']
           # Is the file a billing file?
           if billingFileMatch.search(filesDict['Key']) is None:
               continue
           else:
               noFileNameMatchesFileNameIdentifier = False
           # extract date from file
           dateMatch = dateExtractionMatch.search(filesDict['Key'])
           if dateMatch is None:
             raise Exception('Cannot identify date in billing file name ' + filesDict['Key'] + ' with regex = "' + billingFileDateIdentifier + '"')
           date = dateMatch.group(0)
           billDateDatetime = datetime.datetime(*(time.strptime(date, '%Y-%m')[0:6]))
           if self.verboseFlag or self.debugFlag:
               print 'Date extracted from file: ' + billDateDatetime.strftime('%m/%d/%y %H:%M')

           # Start by putting the current file and file start date in the previous list
           if not previousFileNameForDownloadListString:
               previousFileNameForDownloadListString = filesDict['Key']
               previousFileForDownloadListDateTime = billDateDatetime
               if self.debugFlag:
                   print 'previousFileForDownloadListDateTime ' + previousFileForDownloadListDateTime.strftime('%m/%d/%y %H:%M')
                   print 'previousFileNameForDownloadListString ' + previousFileNameForDownloadListString
                   print fileNameForDownloadList
                   print 'previousFileForDownloadListDateTime ' + previousFileForDownloadListDateTime.strftime('%m/%d/%y %H:%M')
                   print 'previousFileNameForDownloadListString ' + previousFileNameForDownloadListString
                   print fileNameForDownloadList
                   print
               continue

           # if the last known bill date is past the start date of the previous file...
           if not lastKnownBillDateDatetime:
              lastKnownBillDateDatetime = previousFileForDownloadListDateTime
           if lastKnownBillDateDatetime > previousFileForDownloadListDateTime:
               if self.debugFlag:
                   print 'lastKnownBillDateDatetime > previousFileForDownloadListDateTime: ' + lastKnownBillDateDatetime.strftime('%m/%d/%y %H:%M') + ' > ' + previousFileForDownloadListDateTime.strftime('%m/%d/%y %H:%M')
               # if the previous file starts and end around the last known bill date,
               # add previous and current file name to the list
               if lastKnownBillDateDatetime < billDateDatetime:
                   fileNameForDownloadList = [ previousFileNameForDownloadListString, filesDict['Key'] ];
                   if self.debugFlag:
                       print 'lastKnownBillDateDatetime < billDateDatetime: ' + lastKnownBillDateDatetime.strftime('%m/%d/%y %H:%M') + ' < ' + billDateDatetime.strftime('%m/%d/%y %H:%M')
                       print 'fileNameForDownloadList:'
                       print fileNameForDownloadList
               previousFileForDownloadListDateTime = billDateDatetime
               previousFileNameForDownloadListString = filesDict['Key']
               if self.debugFlag:
                   print 'previousFileForDownloadListDateTime ' + previousFileForDownloadListDateTime.strftime('%m/%d/%y %H:%M')
                   print 'previousFileNameForDownloadListString ' + previousFileNameForDownloadListString
                   print

           else:
               if not fileNameForDownloadList:
                  fileNameForDownloadList = [ previousFileNameForDownloadListString ]
               # at this point, all the files have a start date past the last known bill date: we want those files
               fileNameForDownloadList.append(filesDict['Key'])
               if self.debugFlag:
                   print 'fileNameForDownloadList:'
                   print fileNameForDownloadList

        if noFileNameMatchesFileNameIdentifier:
           raise Exception('No billing files found in bucket ' + self.bucketBillingName + ' looking for patterns containing ' + billingFileNameIdentifier)

        # After looking at all the files, if their start date is always older than the last known billing date,
        # we take the last file
        if fileNameForDownloadList == []:
            fileNameForDownloadList = [ filesDict['Key'] ]

        if self.verboseFlag or self.debugFlag:
            print 'fileNameForDownloadList:'
            print fileNameForDownloadList

        if len(self.tmpDirForBuillingFiles) and not os.path.exists(self.tmpDirForBuillingFiles):
            os.makedirs(self.tmpDirForBuillingFiles)
        for fileNameForDownload in fileNameForDownloadList:
            fn = os.path.join(self.tmpDirForBuillingFiles, fileNameForDownload)
            s3.download_file(self.bucketBillingName, fileNameForDownload, fn)
        return fileNameForDownloadList

    def _billingDataByMonth(self, zipFileList):
       # Unzip files and aggregate billing info in a single dictionary

       # Since Feb 2016, the csv file has two new field: RecordId (as new 5th column) and
       # ResourceId (last column)
       # If we are merging files with old and new format, we need to add empty
       # columns to preserve the format and allow the cvs module to work properly
       # Here we add the new columns to the old format in any case

       # Constants
       billingFileNameNewFormatIdentifier = '.*with\-resources\-and\-tags\-.*.csv.zip'
       billingFileNameNewFormatMatch = re.compile(billingFileNameNewFormatIdentifier)
       billingFileDateIdentifier = '20[0-9][0-9]\-[0-9][0-9]'
       dateExtractionMatch = re.compile(billingFileDateIdentifier)
       newLastColumnHeaderString = 'ResourceId'
       new5thColumnHeaderString = 'RecordId'
       old4thColumnHeaderString = 'RecordType'
       newFormat = True
       data_by_month = {}
       for zipFileName in zipFileList:
         dateMatch = dateExtractionMatch.search(zipFileName)
         if dateMatch is None:
             raise Exception('Cannot identify date in billing file name %s'%(zipFileName,))
         date_key = dateMatch.group(0)
         data_by_month[date_key] = ''
         # Check if file is in new or old format
         if billingFileNameNewFormatMatch.search(zipFileName) is None:
             newFormat = False
         else:
             newFormat = True

         # Read in files for the merging
         zipFile = zipfile.ZipFile(zipFileName, 'r')
         billingFileName = string.rstrip(zipFileName, '.zip')
         billCSVStr = zipFile.read(billingFileName)
         data_by_month[date_key] = billCSVStr
       return data_by_month

    def _aggregateBillFiles(self, data_by_month):
       # Unzip files and aggregate billing info in a single dictionary

       # Since Feb 2016, the csv file has two new field: RecordId (as new 5th column) and
       # ResourceId (last column)
       # If we are merging files with old and new format, we need to add empty
       # columns to preserve the format and allow the cvs module to work properly
       # Here we add the new columns to the old format in any case

       # Constants
       billCVSAggregateStr = ''
       keylist = data_by_month.keys()
       keylist.sort()
       for k  in keylist:
         billCSVStr = data_by_month[k]
         # Remove the header for all files except the first
         if billCVSAggregateStr != '':
             billCSVStr = re.sub('^.*\n','',billCSVStr,count=1)

         # aggregate data
         billCVSAggregateStr = billCVSAggregateStr + billCSVStr
       if self.debugFlag:
          print billCVSAggregateStr
          print
       return billCVSAggregateStr

#       return list(csv.DictReader(StringIO.StringIO(billCVSAggregateStr)));

    def _sumUpBillFromDateToDate(self, billCVSAggregateStr , sumFromDate, sumToDate = None):
        """
        Sum up bill beginning ``sumFromDate`` and ending ``sumToDate``

        :type billCVSAggregateStr: :obj:`str`
        :arg billCVSAggregateStr: CSV billing information
        :type sumFromDate: :obj:`str`
        :arg sumFromDate: date in format of '%m/%d/%y %H:%M'
        :type sumTomDate: :obj:`str`
        :arg sumTomDate: date in format of '%m/%d/%y %H:%M'


        CSV Billing file format documentation:

        UnBlendedCost : the corrected cost of each item; unblended from the 4 accounts under
        our single master / payer account

        ProductName : S3, EC2, etc

        ItemDescription = contains("data transferred out") holds information about
        charges due to data transfers out

        ItemDescription = EDU_R_FY2015_Q1_LT_FermiNationalAcceleratorLab
        used to account for educational grant discounts. They are negative $ amounts.
        Should be skipped when accumulating cost


        :rtype:  :obj:`dict`

         Returns BillSummaryDict: (Keys depend on services present in the csv file)::

                            {'AmazonSimpleQueueService': 0.0,
                             'AmazonSimpleNotificationService': 0.0,
                             'AWSKeyManagementService': 0.0,
                             'EstimatedTotalDataOut': 0.0033834411000000018,
                             'AmazonElasticComputeCloud': 0.24066755999999997,
                             'AWSCloudTrail': 0.0,
                             'AmazonSimpleStorageService': 0.38619119999999818,
                             'TotalDataOut': 0.0,
                             'Total': 0.62769356699999868,
                             'AWSSupportBusiness': 0.00083480700000000642}
        """

        # Constants
        itemDescriptionCsvHeaderString = 'ItemDescription'
        ProductNameCsvHeaderString = 'ProductName'
        totalDataOutCsvHeaderString = 'TotalDataOut'
        estimatedTotalDataOutCsvHeaderString = 'EstimatedTotalDataOut'
        usageQuantityHeaderString = 'UsageQuantity'
        unBlendedCostCsvHeaderString = 'UnBlendedCost'
        usageStartDateCsvHeaderString = 'UsageStartDate'
        totalCsvHeaderString = 'Total'

        educationalGrantRowIdentifyingString = 'EDU_'
        unauthorizedUsageString = 'Unauthorized Usage' # 'Unauthorized Usage Exposed Key Root:0061992807'
        costOfGBOut = 0.09 # Assume highest cost of data transfer out per GB in $

        sumFromDateDatetime = datetime.datetime(*(time.strptime(sumFromDate, '%m/%d/%y %H:%M')[0:6]))
        lastStartDateBilledConsideredDatetime = sumFromDateDatetime
        if sumToDate != None:
            sumToDateDatetime = datetime.datetime(*(time.strptime(sumToDate, '%m/%d/%y %H:%M')[0:6]))
        BillSummaryDict = { totalCsvHeaderString : 0.0 , totalDataOutCsvHeaderString : 0.0, estimatedTotalDataOutCsvHeaderString : 0.0}

        # The seek(0) resets the csv iterator, in case of multiple passes e.g. in alarm calculations
        billCVSAggregateStrStringIO = StringIO.StringIO(billCVSAggregateStr)
        billCVSAggregateStrStringIO.seek(0)
        for row in csv.DictReader(billCVSAggregateStrStringIO):
            # Skip if there is no date (e.g. final comment lines)
            if row[usageStartDateCsvHeaderString] == '' :
               continue;

            # Skip rows whose UsageStartDate is prior to sumFromDate and past sumToDate
            usageStartDateDatetime = datetime.datetime(*(time.strptime(row[usageStartDateCsvHeaderString], '%Y-%m-%d %H:%M:%S')[0:6]))
            if usageStartDateDatetime < sumFromDateDatetime :
               continue;

            if sumToDate != None:
                if usageStartDateDatetime > sumToDateDatetime :
                    continue;

            if usageStartDateDatetime > lastStartDateBilledConsideredDatetime:
               lastStartDateBilledConsideredDatetime = usageStartDateDatetime

            # Sum up the costs
            try:
                # Don't add up lines that are corrections for the educational grant, the unauthorized usage, or the final Total
                if string.find(row[itemDescriptionCsvHeaderString], educationalGrantRowIdentifyingString) == -1 and \
                   string.find(row[itemDescriptionCsvHeaderString], unauthorizedUsageString) == -1 and \
                   string.find(row[itemDescriptionCsvHeaderString], totalCsvHeaderString) == -1 :
                    key = string.translate(row[ProductNameCsvHeaderString], None, ' ()')

                    # Don't add up lines that don't have a key e.g. final comments in the csv file
                    if key != '':
                        BillSummaryDict[ key ] += float(row[unBlendedCostCsvHeaderString])
                        BillSummaryDict[ totalCsvHeaderString ] += float(row[unBlendedCostCsvHeaderString])
                        # Add up all data transfer charges separately
                        if string.find(row[itemDescriptionCsvHeaderString], 'data transferred out') != -1:
                           BillSummaryDict[ totalDataOutCsvHeaderString ] += float(row[unBlendedCostCsvHeaderString])
                           BillSummaryDict[ estimatedTotalDataOutCsvHeaderString ] += float(row[usageQuantityHeaderString]) * costOfGBOut

            # If it is the first time that we encounter this key (product), add it to the dictionary
            except KeyError:
                BillSummaryDict[ key ] = float(row[unBlendedCostCsvHeaderString])
                BillSummaryDict[ totalCsvHeaderString ] += float(row[unBlendedCostCsvHeaderString])
        return lastStartDateBilledConsideredDatetime, BillSummaryDict;


    def _applyBillCorrections(self, BillSummaryDict):
        """
         Need to apply corrections from the csv files coming from Amazon to reflect the final bill from DLT

         1 The S3 .csv never includes support charges because it isn't available in the
            source data. It can be calculated at the 10% of spend, before applying any
            discounts
         2 the .csv does not include the DLT discount of 7.25%. For all of the non-data
            egress charges, it shows LIST price (DLT Orbitera reflects the discount)
         3 Currently (Nov 2015), the .csv files zero out all data egress costs.
            According to the data egress waiver contract, it is supposed to zero out up to
            15% of the total cost. This correction may need to be applied in the
            future
        """

        # Constants
        vendorDiscountRate = 0.0725 # 7.25%
        supportCostRate = 0.10 # 10%
        adjustedSupportCostKeyString = 'AdjustedSupport'
        adjustedTotalKeyString = 'AdjustedTotal'
        balanceAtDateKeyString = 'Balance'
        totalKeyString = 'Total'

        # Calculate Support cost
        adjustedSupportCost = supportCostRate * BillSummaryDict[ totalKeyString ]

        # Apply vendor discount if funds are NOT on credit
        if self.applyDiscount:
            reductionRateDueToDiscount = 1 - vendorDiscountRate
        else:
            reductionRateDueToDiscount = 1

        CorrectedBillSummaryDict = self.CorrectedBillSummaryDict
        for key in BillSummaryDict:
           CorrectedBillSummaryDict[key] = reductionRateDueToDiscount * BillSummaryDict[key]

        # Add Support cost to the dictionary
        CorrectedBillSummaryDict[adjustedSupportCostKeyString] = adjustedSupportCost

        # Calculate total
        CorrectedBillSummaryDict[adjustedTotalKeyString] = CorrectedBillSummaryDict[ totalKeyString ] + CorrectedBillSummaryDict[adjustedSupportCostKeyString]

        CorrectedBillSummaryDict[balanceAtDateKeyString] = self.balanceAtDate - CorrectedBillSummaryDict[adjustedTotalKeyString]
        self.CorrectedBillSummaryDict = CorrectedBillSummaryDict
        return CorrectedBillSummaryDict


class BillingInfo(Source.Source):
    def __init__(self, *args, **kwargs):
        acconts_config_file = args[0]['billing_configuration']
        self.billing_files_location = args[0]['dst_dir_for_s3_files']
        # Load kown accounts configuration
        account_dict = DEAccountContants.load_constants(acconts_config_file)
        self.accounts = []
        for k, val in account_dict.items():
            self.accounts.append(DEAccountContants.AccountConstants(val))

    def produces(self,schema_id_list):
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
        d = {}
        for i in self.accounts:
            data = {}
            try:
                calculator = AWSBillCalculator(accountName = i.accountName,
                                               accountProfileName = i.credentialsProfileName,
                                               accountNumber = i.accountNumber,
                                               lastKnownBillDate = i.lastKnownBillDate,
                                               #lastKnownBillDate = None,
                                               balanceAtDate = i.balanceAtDate,
                                               applyDiscount = i.applyDiscount,
                                               tmpDirForBuillingFiles = self.billing_files_location,
                                               verboseFlag = False)
                lastStartDateBilledConsideredDatetime, CorrectedBillSummaryDict = calculator.CalculateBill()
                data[i.accountName] = calculator.CorrectedMonthlyBillSummaryList

            except Exception, detail:
                print detail
            except:
                pass
        pandas_data = {}
        if data:
            for k in data:
                keys = data[k][0].keys()
                for key in keys:
                    pandas_data[key] = pd.Series([d[key] for d in data[k]])

        df = pd.DataFrame(pandas_data)
        return { PRODUCES[0]: df }

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"BillingInfo" : {
        "module" :  "modules.AWS.sources.BillingInfo",
        "name"   :  "BillingInfo",
                    "parameters": {
                        "billing_configuration": "%s/de_config/AccountConstants_my.py"%(os.environ.get('HOME'),),
			"dst_dir_for_s3_files":"%s/de_tmp_aws_files"%(os.environ.get('HOME'),),
                    },
        "schedule": 24*60*60,
        }
    }
    account_info = {'AWSRnDAccountConstants':
                    {
                        'lastKnownBillDate': '08/01/16 00:00', # '%m/%d/%y %H:%M'
                        'balanceAtDate': 3839.16,    # $
                        'accountName': 'RnD',
                        'accountNumber': 159067897602,
                        'credentialsProfileName':'BillingRnD',
                        'applyDiscount': True, # DLT discount does not apply to credits
                        'costRatePerHourInLastSixHoursAlarmThreshold': 2, # $ / h # $10/h
                        'costRatePerHourInLastDayAlarmThreshold': 2, # $ / h # $10/h
                        'emailReceipientForAlarms': 'fermilab-cloud-facility-rnd@fnal.gov'
                    }
    }

    print "Entry in channel configuration"
    pprint.pprint(d)
    print "where"
    print "\t name - name of the class to be instantiated by task manager"
    print "\t billing_configuration - configuration requred to get AWS billing information"
    print "\t Example of Billing configuration file:"
    print "-------------"
    pprint.pprint(account_info)
    print "-------------"
    print "\t dst_dir_for_s3_files - directory for AWS billing files"
    print "\t schedule - execution period"


def module_config_info():
    """
    print this module configuration information
    """
    print "produces", PRODUCES
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
        bi = BillingInfo({'billing_configuration':'%s/de_config/AccountConstants_my.py'%(os.environ.get('HOME'),),
                          'dst_dir_for_s3_files':"%s/de_tmp_aws_files"%(os.environ.get('HOME'),)})
        rc = bi.acquire()
        print "INFO"
        print rc


if __name__ == "__main__":
    main()
