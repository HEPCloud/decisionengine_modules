"""
This source takes input from instance_performance_gce.csv
and adds it to data block
"""
import argparse
import pprint

import pandas as pd

from decisionengine.framework.modules import Source
import logging

PRODUCES = ['GCE_Instance_Performance']


class GCEInstancePerformance(Source.Source):

    def __init__(self, config):
        super(GCEInstancePerformance, self).__init__(config)
        self.csv_file = config.get('csv_file')
        if not self.csv_file:
            raise RuntimeError("No csv file found in configuration")
        self.logger = logging.getLogger()

    def produces(self, name_schema_id_list=None):
        return PRODUCES

    def acquire(self):
        return {PRODUCES[0]: pd.read_csv(self.csv_file)}


def module_config_template():
    """
    Print template for this module configuration
    """
    template = {
        'gce_instance_performance': {
            'module': 'decisionengine_modules.GCE.sources.GCEInstancePerformance',
            'name': 'GCEInstancePerformance',
            'parameters': {
                'csv_file': '/path/to/csv_file',
            }
        }
    }
    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print('produces %s' % PRODUCES)
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
