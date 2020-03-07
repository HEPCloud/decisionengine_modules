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

from decisionengine.framework.modules import Source
import logging
import decisionengine_modules.load_config as load_config

# default values
REGION = 'us-west-2'
PRODUCES = ['AWS_Occupancy']


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

    def __cmp__(self, other=None):
        """
        overrides comparison method
        """
        try:
            if (self.data['AvailabilityZone'], self.data['InstanceType']) == (other.data['AvailabilityZone'], other.data['InstanceType']):
                return 0

        except:
            pass

        return -1


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
            self.ec2_resource = boto3.resource('ec2', region)
        self.instance_types = instance_types
        self.account_name = profile_name

    def get_ec2_instances(self):
        """
        Get all known EC2 instances.

        :rtype: :obj:`dict`: return all instances
        """

        instances = self.ec2_resource.instances.all()
        d = {}
        for instance in instances:
            running_vms = 0
            if instance.state['Name'] == 'running':
                running_vms = 1
            d[instance.id] = {'AccountName': self.account_name,
                              'InstanceType': instance.instance_type,
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
                    (self.instance_types and
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


class AWSOccupancy(Source.Source):
    def __init__(self, configdict):
        self.config_file = configdict['occupancy_configuration']
        self.account_dict = {}
        self.logger = logging.getLogger()

    def produces(self, schema_id_list): return PRODUCES

    def acquire(self):
        """
        Fills ``self.data`` with spot price data.

        :type spot_price_history: :obj:`list`
        :arg spot_price_history: list of spotprice data (:class:`SpotPriceData`)
        """

        # Load kown accounts configuration
        # account configuration is dynamic
        self.account_dict = load_config.load(self.config_file, 5, 20)
        occupancy_data = []
        self.logger.debug('account_dict %s' % (self.account_dict,))
        for account in self.account_dict:
            for region in self.account_dict[account]:
                occcupancy = OccupancyForRegion(region, profile_name=account)
                instances = occcupancy.get_ec2_instances()
                if instances:
                    data = occcupancy.capacity(instances)
                    if data:
                        occupancy_data += data

        oc_list = [i.data for i in occupancy_data]
        return {PRODUCES[0]: pd.DataFrame(oc_list)}


def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"AWSOccupancy": {
        "module":  "modules.AWS.sources.AWSOccupancy",
        "name":  "AWSSpotOccupancy",
        "parameters": {
            "occupancy_configuration": "%s/de_config/AWS_occupancy_config.py" % (os.environ.get('HOME'),),
        },
        "schedule": 60*60,
    }
    }

    config = {"ProfileName1":
              ["RegionName1"],
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
        occupancy = AWSOccupancy(
            {'occupancy_configuration': 'occupancy_config_sample.py'})
        rc = occupancy.acquire()
        print "INFO"
        print rc


if __name__ == "__main__":
    main()
