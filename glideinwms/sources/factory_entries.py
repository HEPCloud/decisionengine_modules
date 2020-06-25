
import argparse
from functools import partial
import logging
import pprint
import pandas

from decisionengine.framework.modules import Source
from decisionengine_modules.util.retry_function import retry_wrapper
from decisionengine_modules.htcondor import htcondor_query


PRODUCES = [
    'Factory_Entries_Grid', 'Factory_Entries_AWS',
    'Factory_Entries_GCE', 'Factory_Entries_LCF'
]


class FactoryEntries(Source.Source):

    def __init__(self, config):
        if not config:
            config = {}
        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.condor_config = config.get('condor_config')
        self.factories = config.get('factories', [])
        self._entry_gridtype_map = {
            'Factory_Entries_Grid': ('gt2', 'condor'),
            'Factory_Entries_AWS': ('ec2',),
            'Factory_Entries_GCE': ('gce',),
            'Factory_Entries_LCF': ('batch slurm',)
        }

        # The combination of nretries=10 and retry_interval=2 adds up to just
        # over 15 minutes
        self.nretries = config.get('nretries', 0)
        self.retry_interval = config.get('retry_interval', 0)

        self.subsystem_name = 'any'
        self.logger = logging.getLogger()


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

        dataframe = pandas.DataFrame()

        for factory in self.factories:
            collector_host = factory.get('collector_host')
            constraint = '(%s)&&(glideinmytype=="glidefactory")' % \
                factory.get('constraint', True)
            classad_attrs = factory.get('classad_attrs')

            try:
                condor_status = htcondor_query.CondorStatus(
                    subsystem_name=self.subsystem_name,
                    pool_name=collector_host,
                    group_attr=['GLIDEIN_GridType'])

                retry_wrapper(
                    partial(condor_status.load,
                            *(constraint, classad_attrs, self.condor_config)),
                    nretries=self.nretries,
                    retry_interval=self.retry_interval)

                df = pandas.DataFrame(condor_status.stored_data)
                if not df.empty:
                    (col_host, sec_cols) = htcondor_query.split_collector_host(collector_host)
                    df['CollectorHost'] = [col_host] * len(df)
                    if sec_cols != '':
                        df['CollectorHosts'] = ['%s,%s' % (col_host, sec_cols)] * len(df)
                    else:
                        df['CollectorHosts'] = [col_host] * len(df)

                    dataframe = pandas.concat([dataframe, df], ignore_index=True, sort=True)
            except htcondor_query.QueryError as e:
                self.logger.error('Failed to fetch glidefactory classads '
                                  'from collector host(s) "{}": {}'.format(
                                      collector_host, e))
            except Exception:
                self.logger.exception('Unexpected error fetching glidefactory '
                           'classads from collector host(s) '
                           '"{}"'.format(collector_host))

        results = {}
        if not dataframe.empty:
            for key, value in self._entry_gridtype_map.items():
                results[key] = dataframe.loc[(dataframe.GLIDEIN_GridType.isin(list(value)))]
        else:
            # There were no entry classads in the factory collector or
            # quering the collector failed
            for entry_type in self.produces():
                results[entry_type] = pandas.DataFrame()

        return results


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'factory_entries': {
            'module': 'decisionengine_modules.glideinwms.sources.factory_entries',
            'name': 'FactoryEntries',
            'parameters': {
                'condor_config': '/path/to/condor_config',
                'nretries': 10,
                'retry_interval': 2,
                'factories': [
                    {
                        'collector_host': 'factory_collector.com',
                        'classad_attrs': []
                    },
                    {
                        'collector_host': 'factory_collector-2.com',
                        'classad_attrs': [],
                        'constraints': 'HTCondor classad query constraints',
                    },
                ],
            },
            'schedule': 120,
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
