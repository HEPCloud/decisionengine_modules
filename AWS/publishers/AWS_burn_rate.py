#!/usr/bin/env python
"""
Publishes AWS VM burn rate

"""
import pprint

import decisionengine.framework.dataspace.dataspace as dataspace
import decisionengine.framework.configmanager.ConfigManager as configmanager
from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher

DEFAULT_GRAPHITE_CONTEXT = "hepcloud_priv.de.aws"
CONSUMES = ['AWS_Burn_Rate']

class AWSBurnRatePublisher(publisher):

    def consumes(self):
        return CONSUMES

    def graphite_context(self, data_block):
        d = {}
        # There should be only one row [0] in the AWS_Burn_Rate data block
        d['FERMILAB.BurnRate'] = data_block.loc[0,'BurnRate'].item()
        return self.graphite_context_header, d

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {
        "AWSBurnRatePublisher": {
            "module": "modules.AWS.publishers.AWS_burn_rate",
            "name": "AWSBurnRatePublisher",
        },
    }
    print("Entry in channel configuration")
    pprint.pprint(d)
    print("where")
    print("\t name - name of the class to be instantiated by task manager")
    print("\t publish_to_graphite - publish to graphite if True")
    print("\t graphite_host - graphite host name")

def module_config_info():
    """
    print this module configuration information
    """

    print("consumes", CONSUMES)
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
        config_manager = configmanager.ConfigManager()
        config_manager.load()
        global_config = config_manager.get_global_config()
        print("GLOBAL CONF", global_config)
        ds = dataspace.DataSpace(global_config)

if __name__ == '__main__':
    main()
