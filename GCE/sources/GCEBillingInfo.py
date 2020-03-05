#!/usr/bin/env python
import json
import boto
import argparse
import gcs_oauth2_boto_plugin
import csv
import io
import string
import re
import datetime
import time
import sys
import os
import pprint
import pandas as pd

import logging
from decisionengine.framework.modules import Source
from boto.exception import NoAuthHandlerFound

PRODUCES = ['GCE_Billing_Info']

class GCEBillCalculator(object):
    """
    Calculate GCE bill
    """

    def __init__(self, projectId, accountProfileName, accountNumber, lastKnownBillDate, balanceAtDate, applyDiscount, botoConfig, localFileDir, sumToDate = None):

        self.logger = logging.getLogger()

        # Configuration parameters
        self.project_id = projectId
        self.accountProfileName = accountProfileName
        self.accountNumber = accountNumber
        self.bucketBillingName = 'billing-' + str(self.project_id)
        # Expect lastKnownBillDate as '%m/%d/%y %H:%M' : validated when needed
        self.lastKnownBillDate = lastKnownBillDate
        self.balanceAtDate = balanceAtDate # $
        self.applyDiscount = applyDiscount
        # Expect sumToDate as '%m/%d/%y %H:%M' : validated when needed
        self.botoConfig = botoConfig
        self.localFileDir = localFileDir
        self.sumToDate = sumToDate # '08/31/16 23:59'

        # Do not download the files twice for repetitive calls e.g. for alarms
        self.fileNameForDownloadList = None

        # Set env for google api
        #os.environ['BOTO_CONFIG'] = self.botoConfig 


    def CalculateBill(self):

        # Load data in memory
        if self.fileNameForDownloadList is None:
            self.fileNameForDownloadList = self._downloadBillFiles()

        if self.fileNameForDownloadList != []:
            lastStartDateBilledConsideredDatetime, BillSummaryDict = self._sumUpBillFromDateToDate(self.fileNameForDownloadList, self.lastKnownBillDate, self.sumToDate)
        else:
            return "", {}

        CorrectedBillSummaryDict = self._applyBillCorrections(BillSummaryDict)

        self.logger.debug('---')
        self.logger.debug('Bill Computation for %s Account Finished at %s' % (self.project_id, time.strftime("%c")))
        self.logger.debug('Last Start Date Billed Considered : ' + lastStartDateBilledConsideredDatetime.strftime('%m/%d/%y %H:%M'))
        self.logger.debug('Last Known Balance :' + str(self.balanceAtDate))
        self.logger.debug('Date of Last Known Balance : ' + self.lastKnownBillDate)
        self.logger.debug('BillSummaryDict:')
        self.logger.debug(json.dumps(BillSummaryDict))
        self.logger.debug('CorrectedBillSummaryDict')
        self.logger.debug(json.dumps(CorrectedBillSummaryDict))

        return lastStartDateBilledConsideredDatetime, CorrectedBillSummaryDict


    def _downloadBillFiles(self):
        # Identify what files need to be downloaded, given the last known balance date
        # Download the files from google storage

        # Constants
        # URI scheme for Cloud Storage.
        GOOGLE_STORAGE = 'gs'
        LOCAL_FILE = 'file'
        header_values = {"x-goog-project-id": self.project_id}

        # Access list of files from Goggle storage bucket
        try:
            uri = boto.storage_uri(self.bucketBillingName, GOOGLE_STORAGE)
            file_obj = uri.get_bucket()
        except NoAuthHandlerFound:
            self.logger.error("Unable to download GCE billing file names because auth is not set up")
            return []
        except:
            self.logger.error("Able to auth but unable to download GCE billing files")
            return []

        filesList = []
        for obj in file_obj:
            filesList.append(obj.name)
        # Assumption: sort files by date using file name: this is true if file name convention is maintained
        filesList.sort()

        # Extract file creation date from the file name
        # Assume a format such as this: Fermilab Billing Export-2016-08-22.csv
        # billingFileNameIdentifier = 'Fermilab\ Billing\ Export\-20[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9].csv'
        billingFileNameIdentifier = "hepcloud\-fnal\-20[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9].csv"
        billingFileMatch = re.compile(billingFileNameIdentifier)
        billingFileDateIdentifier = "20[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9]"
        dateExtractionMatch = re.compile(billingFileDateIdentifier)
        lastKnownBillDateDatetime = datetime.datetime(*(time.strptime(self.lastKnownBillDate, '%m/%d/%y %H:%M')[0:6]))

        self.logger.debug('lastKnownBillDate ' + self.lastKnownBillDate)
        fileNameForDownloadList = []
        previousFileForDownloadListDateTime = None
        previousFileNameForDownloadListString = None
        noFileNameMatchesFileNameIdentifier = True
        for file in filesList:
            self.logger.debug('File in bucket ' + self.bucketBillingName + ' : ' + file)
            # Is the file a billing file?
            if billingFileMatch.search(file) is None:
                continue
            else:
                noFileNameMatchesFileNameIdentifier = False
            # extract date from file
            dateMatch = dateExtractionMatch.search(file)
            if dateMatch is None:
                self.logger.error('Cannot identify date in billing file name ' + file + ' with regex = "' + billingFileDateIdentifier + '"')
                return []

            date = dateMatch.group(0)
            billDateDatetime = datetime.datetime(*(time.strptime(date, '%Y-%m-%d')[0:6]))
            self.logger.debug('Date extracted from file: ' + billDateDatetime.strftime('%m/%d/%y %H:%M'))

            # Start by putting the current file and file start date in the previous list
            if not previousFileNameForDownloadListString:
                previousFileNameForDownloadListString = file
                previousFileForDownloadListDateTime = billDateDatetime
                self.logger.debug('previousFileForDownloadListDateTime ' + previousFileForDownloadListDateTime.strftime('%m/%d/%y %H:%M'))
                self.logger.debug('previousFileNameForDownloadListString ' + previousFileNameForDownloadListString)
                self.logger.debug(fileNameForDownloadList)
                continue

            # if the last known bill date is past the start date of the previous file...
            if lastKnownBillDateDatetime > previousFileForDownloadListDateTime:
                self.logger.debug('lastKnownBillDateDatetime > previousFileForDownloadListDateTime: ' + lastKnownBillDateDatetime.strftime('%m/%d/%y %H:%M') + ' > ' + previousFileForDownloadListDateTime.strftime('%m/%d/%y %H:%M'))
                # if the previous file starts and end around the last known bill date,
                # add previous and current file name to the list
                if lastKnownBillDateDatetime < billDateDatetime:
                    fileNameForDownloadList = [previousFileNameForDownloadListString, file]
                    self.logger.debug('lastKnownBillDateDatetime < billDateDatetime: ' + lastKnownBillDateDatetime.strftime('%m/%d/%y %H:%M') + ' < ' + billDateDatetime.strftime('%m/%d/%y %H:%M'))
                    self.logger.debug('fileNameForDownloadList:')
                    self.logger.debug(fileNameForDownloadList)
                previousFileForDownloadListDateTime = billDateDatetime
                previousFileNameForDownloadListString = file
                self.logger.info('previousFileForDownloadListDateTime ' + previousFileForDownloadListDateTime.strftime('%m/%d/%y %H:%M'))
                self.logger.info('previousFileNameForDownloadListString ' + previousFileNameForDownloadListString)

            else:
                if not fileNameForDownloadList:
                    fileNameForDownloadList = [previousFileNameForDownloadListString]
                # at this point, all the files have a start date past the last known bill date: we want those files
                fileNameForDownloadList.append(file)
                self.logger.debug('fileNameForDownloadList:')
                self.logger.debug(fileNameForDownloadList)

        if noFileNameMatchesFileNameIdentifier:
            self.logger.error('No billing files found in bucket ' + self.bucketBillingName + ' looking for patterns containing ' + billingFileNameIdentifier)
            return []

        # After looking at all the files, if their start date is always older than the last known billing date,
        # we take the last file
        if fileNameForDownloadList == []:
            fileNameForDownloadList = [file]

        self.logger.info('fileNameForDownloadList:')
        self.logger.info(fileNameForDownloadList)

        # Download files to the local directory
        dest_dir = self.localFileDir 
        for fileNameForDownload in fileNameForDownloadList:
            try:
                src_uri = boto.storage_uri(self.bucketBillingName + '/' + fileNameForDownload, GOOGLE_STORAGE)
            except NoAuthHandlerFound:
                self.logger.error("Unable to download GCE billing file %s " % fileNameForDownload)
                return []
            except:
                self.logger.error("Able to auth but unable to download billing file %s " % fileNameForDownload)
                return []

            # Create a file-like object for holding the object contents.
            object_contents = io.StringIO()

            # The unintuitively-named get_file() doesn't return the object
            # contents; instead, it actually writes the contents to
            # object_contents.
            src_uri.get_key().get_file(object_contents)

            try:
                local_dst_uri = boto.storage_uri(os.path.join(dest_dir, fileNameForDownload), LOCAL_FILE)
            except Exception as e:
                self.logger.error("Unable to download GCE billing file %s " % fileNameForDownload)
                return []

            object_contents.seek(0)
            local_dst_uri.new_key().set_contents_from_file(object_contents)
            object_contents.close()

        return fileNameForDownloadList


    def _sumUpBillFromDateToDate(self, fileList, sumFromDate, sumToDate = None):
        # CSV Billing file format documentation:
        # https://support.google.com/cloud/answer/6293835?rd=1
        # https://cloud.google.com/storage/pricing
        #
        # Cost : the cost of each item; no concept of "unblended" cost in GCE, it seems.
        #
        # Line Item : The URI of the specified resource. Very fine grained. Need to be grouped
        #
        # Project ID : multiple project billing in the same file
        #
        #  Returns:
        #               BillSummaryDict: (Keys depend on services present in the csv file)

        # Constants
        itemDescriptionCsvHeaderString = 'ItemDescription'
        ProductNameCsvHeaderString = 'Line Item'
        costCsvHeaderString = 'Cost'
        usageStartDateCsvHeaderString = 'Start Time'
        totalCsvHeaderString = 'Total'

        adjustedSupportCostKeyString = 'AdjustedSupport'

        sumFromDateDatetime = datetime.datetime(*(time.strptime(sumFromDate, '%m/%d/%y %H:%M')[0:6]))
        lastStartDateBilledConsideredDatetime = sumFromDateDatetime
        if sumToDate is not None:
            sumToDateDatetime = datetime.datetime(*(time.strptime(sumToDate, '%m/%d/%y %H:%M')[0:6]))
        BillSummaryDict = {totalCsvHeaderString: 0.0, adjustedSupportCostKeyString: 0.0}


        for fileName in fileList:
            file = open(self.localFileDir + fileName, 'rb')
            csvfilereader = csv.DictReader(file)
            rowCounter=0

            for row in csvfilereader:
                # Skip if there is no date (e.g. final comment lines)
                if row[usageStartDateCsvHeaderString] == '':
                    self.logger.error("Missing Start Time in row: ", row)
                    return []

                # Skip rows whose UsageStartDate is prior to sumFromDate and past sumToDate
                # Remove timezone info, as python 2.4 does not support %z and we consider local time
                # Depending on standard vs. daylight time we have a variation on that notation.
                dateInRowStr = re.split('-0[7,8]:00',row[usageStartDateCsvHeaderString])[0]
                usageStartDateDatetime = datetime.datetime(*(time.strptime(dateInRowStr, '%Y-%m-%dT%H:%M:%S')[0:6]))
                if usageStartDateDatetime < sumFromDateDatetime:
                    continue

                if sumToDate is not None:
                    if usageStartDateDatetime > sumToDateDatetime:
                        continue

                if usageStartDateDatetime > lastStartDateBilledConsideredDatetime:
                    lastStartDateBilledConsideredDatetime = usageStartDateDatetime

                # Sum up the costs
                try:
                    rowCounter+=1
                    key = row[ProductNameCsvHeaderString]
                    if key == '':
                        self.logger.error("Missing Line Item in file %s, row: %s" % (fileName, row))
                        return []

                    # For now we do not calculate support costs as they depend on Onix services only

                    # Add up cost per product (i.e. key) and total cost
                    # totalCsvHeaderString already exists within the dictionary: it is added first
                    # as it is guaranteed not to throw a KeyError exception.
                    BillSummaryDict[totalCsvHeaderString] += float(row[costCsvHeaderString])
                    BillSummaryDict[key] += float(row[costCsvHeaderString])


                # If it is the first time that we encounter this key (product), add it to the dictionary
                except KeyError:
                    BillSummaryDict[key] = float(row[costCsvHeaderString])
                except Exception as e:
                    self.logger.error("GCE billing: Unable to sum row %s" % row)
                    return [] 

        return lastStartDateBilledConsideredDatetime, BillSummaryDict

    def _applyBillCorrections(self, BillSummaryDict):
        # Need to apply corrections from the csv files coming from Amazon to reflect the final
        # bill from DLT
        # 1) Support charges seem to be due to support services offered by Onix
        # 2) Do we have any discounts from Onix e.g. DLT gave us 7.25% ?
        # 3) Can we establish a data egress waiver for GCE?
        #
        # This function also aggregates services according to these rules:
        #
        #     SpendingCategory, ItemPattern, Example, Description
        #     compute-engine/instances, compute-engine/Vmimage*, com.google.cloud/services/compute-engine/VmimageN1Standard_1, Standard Intel N1 1 VCPU running in Americas
        #     compute-engine/instances, compute-engine/Licensed*, com.google.cloud/services/compute-engine/Licensed1000206F1Micro, Licensing Fee for CentOS 6 running on Micro instance with burstable CPU
        #     compute-engine/network, compute-engine/Network*, com.google.cloud/services/compute-engine/NetworkGoogleEgressNaNa, Network Google Egress from Americas to Americas
        #     compute-engine/network, compute-engine/Network*, com.google.cloud/services/compute-engine/NetworkInterRegionIngressNaNa, Network Inter Region Ingress from Americas to Americas
        #     compute-engine/network, compute-engine/Network*, com.google.cloud/services/compute-engine/NetworkInternetEgressNaApac, Network Internet Egress from Americas to APAC
        #     compute-engine/storage, compute-engine/Storage*, com.google.cloud/services/compute-engine/StorageImage, Storage Image
        #     compute-engine/storage, compute-engine/Storage*, com.google.cloud/services/compute-engine/StoragePdCapacity, Storage PD Capacity
        #     compute-engine/other, , , everything else w/o examples
        #     cloud-storage/storage, cloud-storage/Storage*, com.google.cloud/services/cloud-storage/StorageStandardUsGbsec, Standard Storage US
        #     cloud-storage/network, cloud-storage/Bandwidth*, com.google.cloud/services/cloud-storage/BandwidthDownloadAmerica, Download US EMEA
        #     cloud-storage/operations, cloud-storage/Class*, com.google.cloud/services/cloud-storage/ClassARequest, Class A Operation Request e.g. list obj in bucket ($0.10 per 10,000)
        #     cloud-storage/operations, cloud-storage/Class*, com.google.cloud/services/cloud-storage/ClassBRequest, Class B Operation Request e.g. get obj ($0.01 per 10,000)
        #     cloud-storage/other, , , everything else w/o examples
        #     pubsub, pubsub/*, com.googleapis/services/pubsub/MessageOperations, Message Operations
        #     services, services/*, , Any other service under com.google.cloud/services/* not currently in the examples

        # Constants
        adjustedSupportCostKeyString = 'AdjustedSupport'
        adjustedTotalKeyString = 'AdjustedTotal'
        balanceAtDateKeyString = 'Balance'
        totalKeyString = 'Total'
        ignoredEntries = ['Total', 'AdjustedSupport']

        # using an array of tuples rather than a dictionary to enforce an order
        # (as soon as there's a match, no other entries are checked: higher priority
        # (i.e. more detailed) categories should be entered first
        # (using regex in case future entries need more complex parsing;
        # (there shouldn't be any noticeable performance loss (actually, regex may even be faster than find()!
        # '/' acts as '.' in graphite (i.e. it's a separator)
        spendingCategories = [('compute-engine.instances', re.compile("com\.google\.cloud/services/compute-engine/(Vmimage|Licensed)")),
                              ('compute-engine.network', re.compile("com\.google\.cloud/services/compute-engine/Network")),
                              ('compute-engine.storage', re.compile("com\.google\.cloud/services/compute-engine/Storage")),
                              ('compute-engine.other', re.compile("com\.google\.cloud/services/compute-engine/")),
                              ('cloud-storage.storage', re.compile("com\.google\.cloud/services/cloud-storage/Storage")),
                              ('cloud-storage.network', re.compile("com\.google\.cloud/services/cloud-storage/Bandwidth")),
                              ('cloud-storage.operations', re.compile("com\.google\.cloud/services/cloud-storage/Class")),
                              ('cloud-storage.other', re.compile("com\.google\.cloud/services/cloud-storage/")),
                              ('pubsub', re.compile("com\.googleapis/services/pubsub/")),
                              ('services', re.compile(''))] # fallback category

        CorrectedBillSummaryDict = dict([(key, 0) for key in [k for k,v in spendingCategories]])
        # use the line above if dict comprehensions are not yet supported
        #CorrectedBillSummaryDict = { key: 0.0 for key in [ k for k,v in spendingCategories ] }

        for entryName, entryValue in BillSummaryDict.items():
            if entryName not in ignoredEntries:
                for categoryName, categoryRegex in spendingCategories:
                    if categoryRegex.match(entryName):
                        try:
                            CorrectedBillSummaryDict[categoryName] += entryValue
                        except KeyError:
                            CorrectedBillSummaryDict[categoryName] = entryValue
                        break

        # Calculate totals
        CorrectedBillSummaryDict[adjustedSupportCostKeyString] = BillSummaryDict[adjustedSupportCostKeyString]
        CorrectedBillSummaryDict[adjustedTotalKeyString] = BillSummaryDict[totalKeyString] + BillSummaryDict[adjustedSupportCostKeyString]
        CorrectedBillSummaryDict[balanceAtDateKeyString] = self.balanceAtDate - CorrectedBillSummaryDict[adjustedTotalKeyString]

        return CorrectedBillSummaryDict


class GCEBillingInfo(Source.Source):
    def __init__(self, config):
        super(GCEBillingInfo, self).__init__(config)

        # Load configuration "constants"
        self.projectId = config.get('projectId') 
        self.credentialsProfileName = config.get('credentialsProfileName') # NOT CURRENTLY USED
        self.accountNumber = config.get('accountNumber') # NOT CURRENTLY USED
        self.lastKnownBillDate = config.get('lastKnownBillDate') # '%m/%d/%y %H:%M'
        self.balanceAtDate = config.get('balanceAtDate') # $
        self.applyDiscount = config.get('applyDiscount') # Onix does not provide discounts
        self.botoConfig = config.get('botoConfig') # BOTO_CONFIG env
        self.localFileDir = config.get('localFileDir') # location for downloaded billing files

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

        try:
            calculator = GCEBillCalculator(projectId = self.projectId,
                                           accountProfileName = self.credentialsProfileName,
                                           accountNumber = self.accountNumber,
                                           lastKnownBillDate = self.lastKnownBillDate,
                                           balanceAtDate = self.balanceAtDate,
                                           applyDiscount = self.applyDiscount,
                                           botoConfig = self.botoConfig,
                                           localFileDir = self.localFileDir)
#                                           sumToDate = '10/20/16 23:59')


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
            "module":  "modules.GCE.sources.GCEBillingInfo",
            "name":  "GCEBillingInfo",
            "parameters": {
                'projectId': 'Blah',
                'lastKnownBillDate': '01/01/18 00:00', # '%m/%d/%y %H:%M'
                'balanceAtDate': 100.0,    # $
                'accountName': 'Blah',
                'accountNumber': 1111,
                'credentialsProfileName':'BillingBlah',
                'applyDiscount': True, # DLT discount does not apply to credits
                'botoConfig': "path_to_file",
                'locaFileDir': "dir_for_billing_files"
            },
            "schedule": 24*60*60,
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
