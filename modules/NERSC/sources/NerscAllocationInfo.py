"""
Get allocation info from Nersc
"""
import argparse
import pprint

import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.modules.NERSC.util import newt
import decisionengine.framework.modules.de_logger as de_logger

PRODUCES = ['Nersc_Allocation_Info']

class NerscAllocationInfo(Source.Source):

    """
    Information of allocations on NERSC machines
    """

    def __init__(self, config):

        self.constraints = config.get('constraints')
        if not isinstance(self.constraints, dict):
            raise RuntimeError('constraints should be a dict')

        self.raw_results = None
        self.pandas_frame = None
        self.newt = newt.Newt(config.get('passwd_file'))
        self.logger = de_logger.get_logger()

    def send_query(self):
        """
        Send queries and then filter the results based on user constraints
        """
        results = []

        for username in self.constraints['usernames']:
            values = self.newt.get_usage(username)
            if values: 
                results.extend(values['items'])

        # filter results based on 'repo_names' and 'repo_types'

        self.raw_results = filter(lambda x : x['rname'] in self.constraints.get('repo_names',[]) and
                                  x['repo_type'] in self.constraints.get('repo_types',[]),
                                  results)

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
