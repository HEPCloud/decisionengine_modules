#!/usr/bin/env python
"""
Publishes GCE VM Burn Rates

"""
import argparse
import pprint

from decisionengine_modules.graphite.publishers.generic_publisher import GenericPublisher as publisher
from decisionengine.framework.modules import de_logger

DEFAULT_GRAPHITE_CONTEXT = "hepcloud_priv.de.gce"
CONSUMES = ['GCE_Burn_Rate']

class GCEBurnRatePublisher(publisher):
    def __init__(self, config):
        super(GCEBurnRatePublisher, self).__init__(config)
        self.logger = de_logger.get_logger()

    def consumes(self):
        return CONSUMES

    def graphite_context(self, data_block):
        d = {}
        # Only one row in this data frame but we borrow
        # the iteration method from other publishers
        for i, row in data_block.iterrows():
            d['hepcloud-fnal.BurnRate'] = row['BurnRate']
        return self.graphite_context_header, d

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {
        "GCEBurnRatePublisher": {
            "module": "modules.GCE.publishers.GCEBurnRate_publisher",
            "name": "GCEBurnRatePublisher",
        },
    }
    print "Entry in channel configuration"
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
