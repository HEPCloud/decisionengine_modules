#!/usr/bin/python
import argparse
import pprint
import pandas
import numpy

from decisionengine.modules.htcondor import source


PRODUCES = ['Parameter_Store_Facts']


class ParameterStore():

    def __init__ (self, *args, **kwargs):
        if args:
            config = args[0]
        else:
            config = {}

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')
        self.param_store_file = config.get('param_store_file')


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def acquire(self):
        param_store = {}
        with open(self.param_store_file, 'r') as fd:
            for line in fd.readlines():
                line = line.strip()
                token = line.split('=')
                if len(token) > 1:
                    param_store[token[0].strip()] = '='.join(token[1:]).strip()
                else:
                    #print 'WARN: Ignoring malformed line: %s' % line
                    pass
        return {PRODUCES[0]: pandas.DataFrame([param_store])}


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'parameter_store': {
            'module': 'modules.glideinwms.s_parameter_store',
            'name': 'ParameterStore',
            'parameters': {
                'param_store_file': '/path/to/param_store_file',
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
