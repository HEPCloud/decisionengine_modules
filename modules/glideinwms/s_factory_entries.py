#!/usr/bin/python

import argparse
import pprint
import pandas
import numpy

from decisionengine.framework.modules import Source
from decisionengine.modules.htcondor import htcondor_query


PRODUCES = [
    'Factory_Entries_Grid', 'Factory_Entries_AWS',
    'Factory_Entries_GCE', 'Factory_Entries_LCF'
]


class FactoryEntries(Source.Source):

    def __init__(self, *args, **kwargs):
        if args:
            config = args[0]
        else:
            config = {}

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')
        self.collector_host = config.get('collector_host')
        self.condor_config = config.get('condor_config')
        self.constraint = config.get('constraint', True)
        self.classad_attrs = config.get('classad_attrs')
        self._entry_gridtype_map = {
            'gt2': 'Factory_Entries_Grid',
            'ec2': 'Factory_Entries_AWS',
            'gce': 'Factory_Entries_GCE',
            'batch *': 'Factory_Entries_LCF',
        }


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def acquire(self):
        """
        Acquire factory entries from the factory collector
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        condor_status = htcondor_query.CondorStatus(
            subsystem_name='any',
            pool_name=self.collector_host,
            group_attr=['GLIDEIN_GridType'])

        constraint = '(%s)&&(glideinmytype=="glidefactory")' % self.constraint
        condor_status.load(constraint, self.classad_attrs, self.condor_config)

        results = {}
        for key, value in condor_status.stored_data.iteritems():
            entry_type = key[0].lower()
            if entry_type in self._entry_gridtype_map:
                results[self._entry_gridtype_map[entry_type]] = pandas.DataFrame(value)
            else:
                print('WARNING: No mapping found for entry_type %s, ignoring.' % entry_type)

        return results


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'factory_entries': {
            'module': 'modules.glideinwms.factory_entries',
            'name': 'FactoryEntries',
            'parameters': {
                'collector_host': 'factory_collector.com',
                'condor_config': '/path/to/condor_config',
                'constraints': 'HTCondor classad query constraints',
                'classad_attrs': '[]',
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
