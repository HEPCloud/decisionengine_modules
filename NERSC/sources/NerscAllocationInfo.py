"""
Get allocation info from Nersc
"""
import argparse
import pprint

import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine_modules.NERSC.util import newt
import logging

PRODUCES = ['Nersc_Allocation_Info']

_MAX_RETRIES = 10
_RETRY_BACKOFF_FACTOR = 1


class NerscAllocationInfo(Source.Source):

    """
    Information of allocations on NERSC machines
    """

    def __init__(self, config):
        super().__init__(config)

        self.constraints = config.get('constraints')
        if not isinstance(self.constraints, dict):
            raise RuntimeError('constraints should be a dict')

        self.raw_results = None
        self.max_retries = config.get("max_retries", _MAX_RETRIES)
        self.retry_backoff_factor = config.get("retry_backoff_factor",
                                               _RETRY_BACKOFF_FACTOR)
        self.newt = newt.Newt(
            config.get('passwd_file'),
            num_retries=self.max_retries,
            retry_backoff_factor=self.retry_backoff_factor)
        self.logger = logging.getLogger()

    def send_query(self):
        """
        Send queries and then filter the results based on user constraints
        """
        results = []
        for username in self.constraints.get("usernames", []):
            values = self.newt.get_usage(username)
            if values:
                try:
                    results.extend(values['items'])
                except KeyError:
                    # Empty return from get_usage, so just move on
                    pass
        # filter results based on constraints specified in newt_keys dictionary
        newt_keys = self.constraints.get("newt_keys", {})
        for key, values in newt_keys.items():
            k = key
            # The below remapping is needed for backward compatibility with
            # existing config files
            if key == 'rname':
                k = 'repoName'
            if key == 'repo_type':
                k = 'repoType'
            if values:
                results = [x for x in results if x[k] in values]
        self.raw_results = results

    def produces(self, name_schema_id_list=None):
        """
        Method to be called from Task Manager.
        Copied from Source.py
        """
        return PRODUCES

    def acquire(self):
        """
        Method to be called from Task Manager.
        redefines acquire from Source.py.
        Acquire NERSC allocation info and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """
        self.send_query()
        return {PRODUCES[0]: pd.DataFrame(self.raw_results)}


def module_config_template():
    """
    Print template for this module configuration
    """
    template = {
        'nersc_allocation_info': {
            'module': 'decisionengine_modules.NERSC.sources.NerscAllocationInfo',
            'name': 'NerscAllocationInfo',
            'parameters': {
                'passwd_file': '/path/to/password_file',
                'max_retries': 10,
                'retry_backoff_factor': 1,
                'constraints': {
                    'usernames': ['user1', 'user2'],
                    'newt_keys': {
                        'rname': ['m2612', 'm2696'],
                        'repo_type': ["STR", ],
                    }
                }
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
    parser.add_argument(
        '--acquire-with-config',
        action='store',
        metavar='CONFIG_FILE',
        help='Tries to contact NERSC with the provided config file and pulls '
        'data according to config')
    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    elif args.acquire_with_config:
        from ast import literal_eval
        with open(args.acquire_with_config, 'r') as f:
            config_string = "".join(f.readlines())
            config = literal_eval(config_string)
        n = NerscAllocationInfo(config['sources']['NerscAllocationInfo']
                                ['parameters'])
        print(n.acquire())
    else:
        pass


if __name__ == '__main__':
    main()
