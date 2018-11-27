#!/usr/bin/env python
"""
Query Resource Limits from another channel with the factory source
"""
import pprint
import pandas as pd
import argparse

from decisionengine.framework.modules import SourceProxy
import decisionengine.framework.modules.de_logger as de_logger

PRODUCES = ['GCE_Resource_Limits']


class GCEResourceLimits(SourceProxy.SourceProxy):
    """
    Consumes factory data to find GCE entry limits 
    """
    def __init__(self, config):
        super(GCEResourceLimits, self).__init__(config)
        self.entry_limit_attrs = config.get('entry_limit_attrs')
        self.logger = de_logger.get_logger()

    def produces(self, name_schema_id_list=None):
        """
        Return list of items produced
        """
        return PRODUCES

    def acquire(self):
        """
        Acquire google factory entry limits from source proxy
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        factory_data = super(GCEResourceLimits, self).acquire()
        df_factory_data = factory_data.get(self.data_keys[0])
        df_entry_limits = df_factory_data[self.entry_limit_attrs]
        return {PRODUCES[0]: df_entry_limits}


def module_config_template():
    """
    print a template for this module configuration data
    """

    template = {
        "gce_resource_limits": {
            "module": "modules.GCE.sources.GCEResourceLimits",
            "name":   "GCEResourceLimits",
                      "parameters": {
                        "channel_name": "source_channel_name",
                        "data_products": "list of data keys to retrieve from source channel data",
                        "retries": "<number of retries to acquire data>",
                        "retry_timeout": "<retry timeout>",
                        "entry_limit_attrs": "[]"
                      },
        }
    }

    print "Entry in channel cofiguration"
    pprint.pprint(template)

def module_config_info():
    """
    Print module information
    """
    print 'produces %s' % PRODUCES
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


if __name__ == "__main__":
    main()
