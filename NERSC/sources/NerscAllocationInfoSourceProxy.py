#!/usr/bin/python

import pprint
import argparse

from decisionengine.framework.modules import SourceProxy


PRODUCES = ['Nersc_Allocation_Info']


class NerscAllocationInfoSourceProxy(SourceProxy.SourceProxy):

    def produces(self):
        return PRODUCES

    def acquire(self):
        """
        Acquire factory entries from the factory collector
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        nerscai = super(NerscAllocationInfoSourceProxy, self).acquire()
        if not set(PRODUCES).issubset(set(nerscai.keys())):
            raise RuntimeError('SourceProxy %s not configured with all dataproducts %s' % (
                type(self).__name__, PRODUCES))
        return {'Nersc_Allocation_Info': nerscai.get('Nersc_Allocation_Info')}


def module_config_template():
    """
    print a template for this module configuration data
    """

    template = {
        'NerscAllocationInfoSourceProxy': {
            'module': 'decisionengine_modules.NERSC.sources.NerscAllocationInfoSourceProxy',
            'name': 'NerscAllocationInfoSourceProxy',
            'parameters': {
                'channel_name': 'source_channel_name',
                'Dataproducts': PRODUCES,
                'retries': '<number of retries to acquire data>',
                'retry_timeout': '<retry timeout>'
            }
        }
    }

    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    print this module configuration information
    """

    print("produces", PRODUCES)
    module_config_template()


def main():
    """
    Call this a a test unit or use as CLI of this module
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--configtemplate",
                        action="store_true",
                        help="prints the expected module configuration")

    parser.add_argument("--configinfo",
                        action="store_true",
                        help="prints config template along with produces and consumes info")

    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()


if __name__ == "__main__":
    main()
