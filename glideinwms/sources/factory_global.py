#!/usr/bin/python
import argparse
import pprint
import pandas
import numpy

from decisionengine_modules.htcondor.sources import source


PRODUCES = ['factoryglobal_manifests']


class FactoryGlobalManifests(source.ResourceManifests):

    def __init__(self, *args, **kwargs):
        super(FactoryGlobalManifests, self).__init__(*args, **kwargs)
        self.constraint = '(%s)&&(glideinmytype=="glidefactoryglobal")' % self.constraint
        self.subsystem_name = 'any'


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def acquire(self):
        return {PRODUCES[0]: self.load()}


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'factoryglobal_manifests': {
            'module': 'decisionengine_modules.glideinwms.sources.factory_client',
            'name': 'FactoryGlobalManifests',
            'parameters': {
                'collector_host': 'factory_collector.com',
                'condor_config': '/path/to/condor_config',
                'classad_attrs': [],
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
