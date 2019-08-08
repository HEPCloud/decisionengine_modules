#!/usr/bin/env python
"""
Get AWS spot price information
"""

import datetime
import sys
import os
import time
import copy
import numpy as np
import pandas as pd
import pprint
import boto3

import decisionengine.framework.modules.SourceProxy as SourceProxy
import logging
import decisionengine_modules.load_config as load_config

# default values
REGION = 'us-west-2'
INSTANCE_TYPES = ['m3.2xlarge', 'c3.2xlarge']
HISTORY_OBSERVATION_TIME = 3600 # observe spot price for the last hour
#HISTORY_START_TIME = HISTORY_END_TIME.replace(day=(HISTORY_END_TIME.day-1)) # 1 day ago
PRODUCT_DESCRIPTIONS = ['Linux/UNIX']
DRY_RUN = False
MAX_RESULTS = 1000
AVAILABILITY_ZONE='' # any
PRODUCES = ['provisioner_resource_spot_prices']

class SpotPriceData(object):
    """
    Spot Price data element
    """

    def __init__(self, sp_data):
        """

        :type sp_data: :obj:`dict`
        :arg sp_data: spot price data
        """
        self.data = sp_data
        self.data['Timestamp'] = sp_data['Timestamp'].isoformat()

    def __cmp__(self, other = None):
        """
        overrides comparison method
        """
        try:
            if (self.data['AvailabilityZone'], self.data['InstanceType'])  == (other.data['AvailabilityZone'], other.data['InstanceType']):
                return 0
        except:
            pass

        return -1

class AWSSpotPriceForRegion(object):
    """
    Spot price data and methods
    """
    def __init__(self, region = REGION, profile_name=None):
        """

        :type region: :obj:`str`
        :arg region: AWS region name
        :type profile_name: :obj:`str`
        :arg profile_name: legal AWS profile name
        """
        if profile_name:
            session = boto3.session.Session(profile_name=profile_name,
                                            region_name=region)
            self.ec2 = session.client('ec2', region_name=region)

        else:
            self.ec2 = boto3.client('ec2', region_name = region)
        self.account_name = profile_name
        t = time.time()
        self.start_time = datetime.datetime.utcfromtimestamp(t - HISTORY_OBSERVATION_TIME)
        self.end_time = datetime.datetime.utcfromtimestamp(t)
        self.intance_types = INSTANCE_TYPES
        self.dry_run = DRY_RUN
        self.max_results = MAX_RESULTS
        self.product_descriptions = PRODUCT_DESCRIPTIONS
        self.availability_zone = AVAILABILITY_ZONE

    def init_query(self,
                   spot_price_history_start_time = None,
                   spot_price_history_end_time = None,
                   instance_types = INSTANCE_TYPES,
                   product_descriptions = PRODUCT_DESCRIPTIONS,
                   dry_run = DRY_RUN,
                   max_resuts = MAX_RESULTS,
                   availability_zone = AVAILABILITY_ZONE):

        """
        Init AWS spot price query

        :type spot_price_history_start_time: :obj:`str`
        :arg spot_price_history_start_time: price since.
        :type spot_price_history_end_time: :obj:`str`
        :arg spot_price_history_end_time: price till.
        :type instance_types: :obj:`list`
        :arg instance_types: list of AWS instance types to query spot price for.
        :type dry_run: :obj:`bool`
        :arg dry_run: as described in boto3 documentation.
        :type max_resuts: :obj:`int`
        :arg max_resuts: maximum number of results to return.

        """
        if spot_price_history_start_time:
            self.start_time = spot_price_history_start_time
        if spot_price_history_end_time:
            self.end_time = spot_price_history_end_time
        self.intance_types = instance_types
        self.dry_run =  dry_run
        self.max_results = max_resuts
        self.product_descriptions = product_descriptions
        self.availability_zone = availability_zone


    def get_price(self):
        """
        Get AWS spot prices.
        """
        try:
            rc = self.ec2.describe_spot_price_history(
                DryRun = self.dry_run,
                StartTime = self.start_time,
                EndTime = self.end_time,
                InstanceTypes = self.intance_types,
                ProductDescriptions = self.product_descriptions,
                Filters = [],
                AvailabilityZone = self.availability_zone,
                MaxResults = self.max_results,
                NextToken = '')
        except Exception, e:
            print "Exception", e
            return None
        price_history = rc.get('SpotPriceHistory')
        if len(price_history) == 0:
            price_history = None
        return price_history

    def spot_price_summary(self, spot_price_history):
        """
        Returns the current spot prices per
        availability zone and instance type

        :type spot_price_history: :obj:`list`
        :arg spot_price_history: list of dictonaries
        :rtype: :obj:`list`: list of spot price data (:class:`SpotPriceData`)
        """

        l = []
        for item in spot_price_history:
            item['AccountName'] = self.account_name
            spd = SpotPriceData(item)
            if not spd in l:
                # append if there is no element with given
                # availability zone and instance type
                l.append(spd)
            else:
                # replace spot price by the most recent
                i = l.index(spd)
                l[i].data['Timestamp'] = spd.data['Timestamp']
                l[i].data['SpotPrice'] = spd.data['SpotPrice']
        return l

class AWSSpotPrice(SourceProxy.SourceProxy):
    def __init__(self, *args, **kwargs):
        super(AWSSpotPrice, self).__init__(*args, **kwargs)

    def produces(self,schema_id_list): return PRODUCES

    def acquire(self):
        """
        Gets data from AWS

        :rtype: pandas frame (:class:`pd.DataFramelist`)
        """

        # Load known accounts configuration
        account_conf = super(AWSSpotPrice, self).acquire()
        if len(account_conf.keys()) != 1:
            raise RuntimeError('Wrong configuration %s. Only one key is expected'%(account_conf,))
        self.account_dict = {}
        for k in account_conf:
            self.account_dict = account_conf[k].to_dict()
        sp_data = []
        for account in self.account_dict:
            for region, instances in self.account_dict[account].items():
                spot_price_info = AWSSpotPriceForRegion(region, profile_name=account)
                spot_price_info.init_query(instance_types = instances)
                spot_price_history = spot_price_info.get_price()
                if spot_price_history:
                    sp_data += spot_price_info.spot_price_summary(spot_price_history)

        sp_list = [i.data for i in sp_data]

        return {PRODUCES[0]: pd.DataFrame(sp_list)}

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"AWSSpotPrice": {
        "module" :  "modules.AWS.sources.AWSSpotPriceWithSourceProxy",
        "name"   :  "AWSSpotPrice",
                    "parameters": {
                        "channel_name": "source_channel_name",
                        "Dataproducts": "list of data keys to retrieve from source channel data",
                        "retries": "<number of retries to acquire data>",
                        "retry_timeout": "<retry timeout>"
                    },
        "schedule": 60*60,
        }
    }

    config = {"ProfileName1":
              {"RegionName1":["Instance1",],},
    }

    print "Entry in channel cofiguration"
    pprint.pprint(d)
    print "where"
    print "\t name - name of the class to be instantiated by task manager"
    print "\t spot_price_configuration - configuration required to get AWS spot price information"
    print "\t Example:"
    print "-------------"
    pprint.pprint(config)
    print "where"
    print "\t ProfileName1 - name of account profile (example: hepcloud-rnd)"
    print "\t RegionName1 - name of region (example: us-west-2)"
    print "\t Instance1 - name of instance. If the list of instances is empty, price information for all instances is acquired"

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
        sprice = AWSSpotPrice({"channel_name": "channel_aws_config_data",
                               "Dataproducts":["spot_occupancy_config"],
                               "retries": 3,
                               "retry_timeout": 20,
                           })
        rc = sprice.acquire()
        print "INFO"
        print rc


if __name__ == "__main__":
    main()

