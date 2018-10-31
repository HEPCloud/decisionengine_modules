#!/usr/bin/env python
"""
Publishes price / performance data

"""
import os
import copy
import pprint
import pandas as pd

from decisionengine_modules.graphite.publishers.generic_publisher import GenericPublisher as publisher
import decisionengine.framework.configmanager.ConfigManager as configmanager
import decisionengine.framework.dataspace.datablock as datablock
import decisionengine.framework.dataspace.dataspace as dataspace
import decisionengine_modules.graphite_client as graphite
from decisionengine.framework.modules import de_logger

DEFAULT_GRAPHITE_CONTEXT="hepcloud.de.gce"
CONSUMES=['GCE_Price_Performance']

class GCEPricePerformancePublisher(publisher):
    def __init__(self, config):
        super(GCEPricePerformancePublisher, self).__init__(config)
        self.logger = de_logger.get_logger()

    def consumes(self):
        return CONSUMES

    def graphite_context(self, datablock):
        d = {}
        for i, row in datablock.iterrows():
            key = ('%s.price_perf'%(graphite.sanitize_key(row['EntryName'])))
            d[key] = row['PricePerformance']
        return self.graphite_context_header, d

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"GCEPricePerformancePublisher": {
         "module": "modules.GCE.publishers.GCEPricePerformance_publisher",
         "name": "GCEPricePerformancePublisher",
         },}
    print "Entry in channel cofiguration"
    pprint.pprint(d)
    print "where"
    print "\t name - name of the class to be instantiated by task manager"
    print "\t publish_to_graphite - publish to graphite if True"
    print "\t graphite_host - graphite host name"

def module_config_info():
    """
    print this module configuration information
    """

    print "consumes", CONSUMES
    module_config_template()



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configtemplate',
        action='store_true',
        help='prints the expected module configuration')

    parser.add_argument(
        '--configinfo',
        action='store_true',
        help='prints config template along with produces and consumes info')
    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == '__main__':
    main()
