#!/usr/bin/python
import argparse
import pprint
import pandas
import numpy

from decisionengine.modules.htcondor import publisher

CONSUMES = [
    'glideclient_manifests', 'glideresource_manifests',
]


class GlideinWMSManifests(publisher.HTCondorManifests):

    def __init__(self, *args, **kwargs):
        super(GlideinWMSManifests, self).__init__(*args, **kwargs)


    def consumes(self):
        """
        Return list of items produced
        """
        return CONSUMES


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'glideinwms_manifests': {
            'module': 'modules.glideinwms.p_glideinwms_classads',
            'name': 'GlideinWMSManifests',
            'parameters': {
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
