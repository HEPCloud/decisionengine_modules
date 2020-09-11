import argparse
import numpy
import pandas
import pprint
import traceback
from decisionengine_modules.htcondor.sources import source
from decisionengine_modules.htcondor import htcondor_query

PRODUCES = ['startd_manifests']


class StartdManifests(source.ResourceManifests):

    def __init__(self, config):
        super(StartdManifests, self).__init__(config)
        if not config:
            config = {}
        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.correction_map = self.parameters.get('correction_map')

    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def acquire(self):
        return {PRODUCES[0]: self.load()}

    def load(self):
        """
        Acquire resource classads from the HTCondor Collector
        :rtype: :obj:`~pd.DataFrame`
        """

        dataframe = pandas.DataFrame()
        try:
            condor_status = htcondor_query.CondorStatus(
                subsystem_name=self.subsystem_name,
                pool_name=self.collector_host,
                group_attr=self.group_attr)

            condor_status.load(self.constraint, self.classad_attrs,
                               self.condor_config)

            for eachDict in condor_status.stored_data:
                for eachKey, eachVal in eachDict.items():
                    if (eachVal is None) or (isinstance(eachVal, float) and (eachVal is numpy.nan)):
                        eachDict[eachKey] = self.correction_map[eachKey]

            dataframe = pandas.DataFrame(condor_status.stored_data)
            if not dataframe.empty:
                (collector_host, secondary_collectors) = htcondor_query.split_collector_host(self.collector_host)
                dataframe['CollectorHost'] = [collector_host] * len(dataframe)
                if secondary_collectors != '':
                    dataframe['CollectorHosts'] = ['%s,%s' % (collector_host, secondary_collectors)] * len(dataframe)
                else:
                    dataframe['CollectorHosts'] = [collector_host] * len(dataframe)
        except htcondor_query.QueryError:
            self.logger.warning('Query error fetching classads from collector host(s) "%s"' % self.collector_host)
            self.logger.error('Query error fetching classads from collector host(s) "%s". Traceback: %s' % (self.collector_host, traceback.format_exc()))
        except Exception:
            self.logger.warning('Unexpected error fetching classads from collector host(s) "%s"' % self.collector_host)
            self.logger.error('Unexpected error fetching classads from collector host(s) "%s". Traceback: %s' % (self.collector_host, traceback.format_exc()))

        return dataframe

def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'startd_manifests': {
            'module': 'modules.htcondor.s_slots',
            'name': 'StartdManifests',
            'parameters': {
                'collector_host': 'factory_collector.com',
                'condor_config': '/path/to/condor_config',
                'constraints': 'HTCondor collector query constraints',
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
