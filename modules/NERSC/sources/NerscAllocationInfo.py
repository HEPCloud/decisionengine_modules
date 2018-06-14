#!/usr/bin/python
"""
Get allocation info from Nersc
"""
import argparse
import pprint

import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.modules.NERSC.sources import newt_query

PRODUCES = ['Nersc_Allocation_Info']
ALLOCATION_QUERY_PREFIX = 'https://newt.nersc.gov/newt/account/usage/user/'

class NerscAllocationInfo(Source.Source):

    """
    Information of allocations on NERSC machines
    """

    def __init__(self, config):

        if ('renew_cookie_script' not in config) or ('cookie_file' not in config):
            raise RuntimeError('renew script and cookie file are not passed')

        self.renew_cookie_script = config.get('renew_cookie_script')
        self.cookie_file = config.get('cookie_file')
        self.constraints = config.get('constraints')
        if not isinstance(self.constraints, dict):
            raise RuntimeError('constraints should be a dict')

        self.raw_results = None
        self.pandas_frame = None

    def send_query(self):
        """
        Send queries and then filter the results based on user constraints
        """
        self.raw_results = []

        for username in self.constraints['usernames']:
            query = ALLOCATION_QUERY_PREFIX+username
            values = newt_query.NewtQuery.send_query(
                self.cookie_file, self.renew_cookie_script, query)
            if values != []:
                self.raw_results.extend(values['items'])

        # further filter the results based on 'repo_names' and 'repo_types'
        del_index = []

        for index, value in enumerate(self.raw_results):
            if ((value['rname'] not in self.constraints['repo_names']) or
               (value['repo_type'] not in self.constraints['repo_types'])):
                del_index.append(index)

        for index in sorted(del_index, reverse=True):
            del self.raw_results[index]

    def raw_results_to_pandas_frame(self):
        """
        Convert the acquired external info into Pandas Frame format
        """
        self.pandas_frame = pd.DataFrame(self.raw_results)

    def produces(self):
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
        self.raw_results_to_pandas_frame()
        return {PRODUCES[0]: self.pandas_frame}

def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'nersc_allocation_info': {
            'module': 'framework.modules.NERSC.sources.NerscAllocationInfo',
            'name': 'NerscAllocationInfo',
            'parameters': {
                'renew_cookie_script': '/path/to/script',
                'cookie_file': '/path/to/cookie_file',
                'constraints': {
                    'usernames': '[username1, username 2]',
                    'repo_types': '[STR, REPO]',
                    'repo_names': '[m2612, m2696]',
                }
            }
        }
    }

    print 'Entry in channel configuration'
    pprint.pprint(template)

def module_config_info():
    """
    Print module information
    """
    print 'produces %s' % PRODUCES
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
