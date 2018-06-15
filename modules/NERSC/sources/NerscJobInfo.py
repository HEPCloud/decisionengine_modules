#!/usr/bin/python
"""
Get job info from Nersc
"""
import argparse
import pprint

import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.modules.NERSC.sources import NewtQuery
import decisionengine.framework.modules.de_logger as de_logger

PRODUCES = ['Nersc_Job_Info']
STATUS_QUERY_PREFIX = 'https://newt.nersc.gov/newt/status/'
JOB_QUERY_PREFIX = 'https://newt.nersc.gov/newt/queue/'

class NerscJobInfo(Source.Source):

    """
    Information of jobs on NERSC machines
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
        self.logger = de_logger.get_logger()

    def send_query(self):
        """
        Construct NEWT query strings based on user constraints and then send queries
        """
        self.raw_results = []
        queries = []

        # default, query edison and cori
        if len(self.constraints['machines']) == 0:
            self.constraints['machines'] = ['edison', 'cori']


        # check if the machines listed are down, if so, delete this machine
        for m in self.constraints['machines']:
            q = STATUS_QUERY_PREFIX+m
            values = NewtQuery.NewtQuery.send_query(self.cookie_file, self.renew_cookie_script, q)
            if values != []:
                if values['status'] == 'down':
                    self.constraints['machines'].remove(m)


        # if all machines are down, quit
        if len(self.constraints['machines']) == 0:
            self.raw_results = []
            return

        for m in self.constraints['machines']:
            queries.append(JOB_QUERY_PREFIX+m+'?')

        if len(self.constraints['usernames']) != 0:
            new_list = []
            for u in self.constraints['usernames']:
                for index, q_string in enumerate(queries):
                    s = queries[index] + 'user=' + u + '&'
                    new_list.append(s)
            queries = new_list

        if len(self.constraints['partitions']) != 0:
            new_list = []
            for p in self.constraints['partitions']:
                for index, q_string in enumerate(queries):
                    s = queries[index] + 'queue=' + p + '&'
                    new_list.append(s)
            queries = new_list

        if len(self.constraints['accounts']) != 0:
            new_list = []
            for a in self.constraints['accounts']:
                for index, q_string in enumerate(queries):
                    s = queries[index] + 'repo=' + a + '&'
                    new_list.append(s)
            queries = new_list

        for q in queries:
            #self.logger.info("sending query %s to the newtQuery function" %(q))
            values = NewtQuery.NewtQuery.send_query(self.cookie_file, self.renew_cookie_script, q)
            self.raw_results.extend(values)

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
        Acquire NERSC job info and return as pandas frame
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
        'nersc_job_info': {
            'module': 'framework.modules.NERSC.sources.NerscJobInfo',
            'name': 'NerscJobInfo',
            'parameters': {
                'renew_cookie_script': '/path/to/script',
                'cookie_file': '/path/to/cookieFile',
                'constraints': {
                    'machines': '[machine1, machine2]',
                    'partitions': '[partition1, partition2]',
                    'usernames': '[username1, username 2]',
                    'accounts': '[account1, account2]'
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
    print 'produces %s' % (PRODUCES)
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
