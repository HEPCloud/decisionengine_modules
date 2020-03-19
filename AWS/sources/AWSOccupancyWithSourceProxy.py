#!/usr/bin/env python
"""
Get AWS capacity (running instances) information.
"""
import boto3
import sys
import os
import time
import pprint
import numpy as np
import pandas as pd

import decisionengine.framework.modules.SourceProxy as SourceProxy
import logging
import decisionengine_modules.load_config as load_config

# default values
REGION = 'us-west-2'
PRODUCES = ['AWS_Occupancy']
# TODO this is a default column list and needs to be overriden from configuration
COLUMN_LIST = ['AccountName', 'AvailabilityZone', 'InstanceType', 'RunningVms']
class OccupancyData(object):
    """
    Occupancy data element
    """

    def __init__(self, occupancy_data):
        """

        :type occupancy_data: :obj:`dict`
        :arg occupancy_data: occupancy data
        """
        self.data = occupancy_data

    def __eq__(self, other = None):
        """
        replaces comparison method
        """
        if not other:
            return False


        return (self.data['AvailabilityZone'], self.data['InstanceType'])  == (other.data['AvailabilityZone'], other.data['InstanceType'])

    def __ne__(self, other):
        return not self == other


class OccupancyForRegion(object):
    """
    AWS capacity data and metods
    """

    def __init__(self, region='us-west-2', profile_name=None, instance_types=[]):
        """

        :type region: :obj:`str`
        :arg region: AWS region name
        :type profile_name: :obj:`str`
        :arg profile_name: legal AWS profile name
        :type instance_types: :obj:`list`
        :arg instance_types: list of AWS instance types to query occupancy.
        """

        if profile_name:
            session = boto3.session.Session(profile_name=profile_name,
                                            region_name=region)
            self.ec2_resource = session.resource('ec2', region_name=region)
        else:
            self.ec2_resource =  boto3.resource('ec2', region)
        self.instance_types = instance_types
        self.account_name = profile_name

    def get_ec2_instances(self):
        """
        Get all known EC2 instances.

        :rtype: :obj:`dict`: return all instances
        """

        instances = self.ec2_resource.instances.all()
        d ={}
        for instance in instances:
            running_vms = 0
            if instance.state['Name'] == 'running':
                running_vms = 1
            d[instance.id] = {'AccountName': self.account_name,
                              'InstanceType' : instance.instance_type,
                              'AvailabilityZone': instance.placement['AvailabilityZone'],
                              'RunningVms': running_vms,
                          }

        return d

    def capacity(self, instances):
        """
        Returns the current running instances data

        :type instances: :obj:`dict`
        :arg instances: instances returned by :meth:`get_ec2_instances`
        :rtype: :obj:`list`: list of spot price data (:class:`aws_data.AWSDataElement`)
        """
        l = []
        for instance, data in instances.items():
            if not self.instance_types or \
                    (self.instance_types and \
                         data['InstanceType'] in self.instance_types):
                occ_data = OccupancyData(data)
                if not occ_data in l:
                    l.append(occ_data)
                else:
                    i = l.index(occ_data)
                    l[i].data['RunningVms'] += occ_data.data['RunningVms']

        return l




    '''
    def fill_capacity_data(self, instances):
        """
        Fills ``self.data`` with current instances information.

        :type instances: :obj:`dict`
        :arg instances: instances returned by :meth:`get_ec2_instances`
        """

        internal_data = self.capacity(instances)

        for row in internal_data:
            self.data.put(AvailabilityZone=row.AvailabilityZone,
                          InstanceType=row.InstanceType,
                          RunningVms=row.RunningVms)
  '''

class AWSOccupancy(SourceProxy.SourceProxy):
    def __init__(self, *args, **kwargs):
        super(AWSOccupancy, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger()

    def produces(self): 
        return PRODUCES

    def acquire(self):
        """
        Fills ``self.data`` with spot price data.

        :type spot_price_history: :obj:`list`
        :arg spot_price_history: list of spotprice data (:class:`SpotPriceData`)
        """

        # Load kown accounts configuration
        account_conf = super(AWSOccupancy, self).acquire()
        if len(account_conf.keys()) != 1:
            raise RuntimeError('Wrong configuration %s. Only one key is expected'%(account_conf,))
        self.account_dict = {}
        for k in account_conf:
            self.account_dict = account_conf[k].to_dict()
        self.logger.debug('account_dict %s'%(self.account_dict,))
        occupancy_data = []
        for account in self.account_dict:
            for region in self.account_dict[account]:
                occcupancy = OccupancyForRegion(region, profile_name=account)
                instances = occcupancy.get_ec2_instances()
                if instances:
                    data = occcupancy.capacity(instances)
                    if data:
                        occupancy_data += data

        oc_list = [i.data for i in occupancy_data]
        # to fix the test failure
        return { PRODUCES[0]: pd.DataFrame(oc_list, columns = COLUMN_LIST)}

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"AWSOccupancy": {
        "module" :  "modules.AWS.sources.AWSOccupancyWithSourceProxy",
        "name"   :  "AWSSpotOccupancy",
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
              ["RegionName1"],
    }

    print("Entry in channel cofiguration")
    pprint.pprint(d)
    print("where")
    print("\t name - name of the class to be instantiated by task manager")
    print("\t spot_price_configuration - configuration required to get AWS spot price information")
    print("\t Example:")
    print("-------------")
    pprint.pprint(config)
    print("where")
    print("\t ProfileName1 - name of account profile (example: hepcloud-rnd)")
    print("\t RegionName1 - name of region (example: us-west-2)")

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
        occupancy = AWSOccupancy({"channel_name": "channel_aws_config_data",
                               "Dataproducts":["spot_occupancy_config"],
                               "retries": 3,
                               "retry_timeout": 20,
                           })
        rc = occupancy.acquire()
        print("INFO")
        print(rc)


if __name__ == "__main__":
    main()

