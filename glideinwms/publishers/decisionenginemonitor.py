#!/usr/bin/python
import argparse
import pprint
import pandas
import numpy

from decisionengine_modules.htcondor.publishers import publisher

CONSUMES = ['decisionenginemonitor_manifests']


class DecisionEngineMonitorManifests(publisher.HTCondorManifests):

    def __init__(self, config):
        super(DecisionEngineMonitorManifests, self).__init__(config)
        self.classad_type = 'glideclientmonitor'


    def consumes(self):
        """
        Return list of items produced
        """
        return CONSUMES


    def create_invalidate_constraint(self, requests_df):
        for collector_host, request_group in requests_df.groupby(['CollectorHost']):
            client_names = set(request_group['GlideClientName'])
            if client_names:
                constraint = '(glideinmytype == "%s") && (stringlistmember(GlideClientName, "%s"))' % (self.classad_type, ','.join(client_names))
                self.invalidate_ads_constraint[collector_host] = constraint


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'decisionenginemonitor_manifests': {
            'module': 'modules.glideinwms.p_decisionenginemonitor',
            'name': 'DecisionEngineMonitorManifests',
            'parameters': {
                'collector_host': 'factory_collector.com',
                'condor_config': '/path/to/condor_config',
            }
        }
    }
    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print('consumes %s' % CONSUMES)
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
