#!/usr/bin/python
import argparse
import pprint
import pandas
import numpy

from decisionengine.framework.modules import Source
from decisionengine_modules.htcondor import htcondor_query


PRODUCES = ['factoryglobal_manifests']


class FactoryGlobalManifests(Source.Source):

    def __init__(self, *args, **kwargs):
        if args:
            config = args[0]
        else:
            config = {}

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')
        self.condor_config = config.get('condor_config')
        self.factories = config.get('factories', [])
        self.subsystem_name = 'any'


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

        dataframe = None

        for factory in self.factories:
            collector_host = factory.get('collector_host')
            constraint = '(%s)&&(glideinmytype=="glidefactoryglobal")' % factory.get('constraint', True)
            classad_attrs = []

            condor_status = htcondor_query.CondorStatus(
                subsystem_name=self.subsystem_name, pool_name=collector_host,
                group_attr=['Name'])

            condor_status.load(constraint, classad_attrs, self.condor_config)
            df = pandas.DataFrame(condor_status.stored_data)
            if not df.empty:
                df['CollectorHost'] = [collector_host] * len(df)

            dataframe = pandas.concat([dataframe, df], ignore_index=True)

        return {PRODUCES[0]: dataframe}


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
