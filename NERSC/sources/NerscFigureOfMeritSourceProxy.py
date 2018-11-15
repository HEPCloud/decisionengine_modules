#!/usr/bin/python

import pprint
import argparse

from decisionengine.framework.modules import SourceProxy


PRODUCES = ['Nersc_Figure_Of_Merit']


class NerscFigureOfMerit(SourceProxy.SourceProxy):


    def __init__(self, config):
        super(NerscFigureOfMerit, self).__init__(config)


    def produces(self):
        return PRODUCES


    def acquire(self):
        """
        Acquire factory entries from the factory collector
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        fom = super(NerscFigureOfMerit, self).acquire()
        if not set(PRODUCES).issubset(set(fom.keys())):
            raise RuntimeError('SourceProxy %s not configured with all dataproducts %s' % (type(self).__name__, PRODUCES))
        return {'Nersc_Figure_Of_Merit': fom.get('Nersc_Figure_Of_Merit')}


def module_config_template():
    """
    print a template for this module configuration data
    """

    template = {
        'NerscFigureOfMerit': {
            'module': 'decisionengine_modules.NERSC.sources.NerscFigureOfMerit',
            'name': 'NerscFigureOfMerit',
            'parameters': {
                'channel_name': 'source_channel_name',
                'Dataproducts': PRODUCES,
                'retries': '<number of retries to acquire data>',
                'retry_timeout': '<retry timeout>'
            }
        }
    }

    print('Entry in channel cofiguration')
    pprint.pprint(template)


def module_config_info():
    """
    print this module configuration information
    """

    print "produces", PRODUCES
    module_config_template()



def main():
    """
    Call this a a test unit or use as CLI of this module
    """
    import argparse
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
