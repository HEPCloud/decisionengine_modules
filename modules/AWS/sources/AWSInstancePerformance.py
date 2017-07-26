#!/usr/bin/env python
"""
Fill in data from Instane Performance CSV file
"""
import pprint
import sys
import os
import csv
import numpy as np
import pandas as pd

from decisionengine.framework.modules import Source
import decisionengine.framework.modules.de_logger as de_logger
import decisionengine.modules.load_config as load_config

PRODUCES = ['Performance_Data']

class AWSInstancePerformance(Source.Source):
    def __init__(self, *args, **kwargs):
        self.data_file = args[0]['data_file']


    def produces(self):
        return PRODUCES

    def acquire(self):
        return {PRODUCES[0]: pd.read_csv(self.data_file).drop_duplicates(subset=[ 'AvailabilityZone', 'InstanceType'], keep='last').reset_index(drop = True)}

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"AWSInstancePerformance": {
        "module" :  "modules.AWS.sources.AWSInstancePerformance",
        "name"   :  "AWSInstancePerformance",
                    "parameters": {
                        "data_file": "%s/de_data/instance_performance.csv"%(os.environ.get('HOME'),),
                    },
        "schedule": 60*60,
        }
    }

    print "Entry in channel cofiguration"
    pprint.pprint(d)
    print "where"
    print "\t name - name of the class to be instantiated by task manager"
    print "\t data_file - CSV cost data file"

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
        perf_info = AWSInstancePerformance({'data_file':'instance_performance_sample.csv'})
        rc = perf_info.acquire()
        d = rc[PRODUCES[0]]
        pd.set_option('display.max_rows', len(d))
        print "INFO"
        print rc


if __name__ == "__main__":
    main()
