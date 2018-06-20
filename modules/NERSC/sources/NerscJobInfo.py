"""
Get job info from Nersc
"""
import argparse
import pprint

import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.modules.NERSC.util import newt
import decisionengine.framework.modules.de_logger as de_logger

PRODUCES = ['Nersc_Job_Info']
STATUS_QUERY_PREFIX = 'https://newt.nersc.gov/newt/status/'
JOB_QUERY_PREFIX = 'https://newt.nersc.gov/newt/queue/'

class NerscJobInfo(Source.Source):

    """
    Information of jobs on NERSC machines
    """

    def __init__(self, config):
        self.constraints = config.get('constraints')
        if not isinstance(self.constraints, dict):
            raise RuntimeError('constraints should be a dict')
        self.newt = newt.Newt(config.get('passwd_file'))
        self.raw_results = None
        self.pandas_frame = None
        self.logger = de_logger.get_logger()


    def send_query(self):
        """
        Construct NEWT query strings based on user constraints and then send queries
        """
        self.raw_results = []

        # default, query edison and cori
        if len(self.constraints['machines']) == 0:
            self.constraints['machines'] = ['edison', 'cori']


        # get all system status

        up_machines = filter(lambda x: x['status'] == 'up', self.newt.get_status())
        
        if not up_machines: 
            self.logger.info("All machines at NERSC are down")
            self.raw_results = []
            return 

        # filter up machines 

        machines = filter(lambda x: x in [ y["system"] for y in up_machines],
                          self.constraints.get('machines'))

        
        if not machines:
            self.logger.info("All requested machines at NERSC are down")
            self.raw_results = []
            return 
           

        for m in machines:
            queries = ["?"]

            if self.constraints.get('usernames'):
                new_list = []
                for u in self.constraints['usernames']:
                    for index, q_string in enumerate(queries):
                        s = queries[index] + 'user=' + u + '&'
                        new_list.append(s)
                queries = new_list
                
                if self.constraints['partitions']:
                    new_list = []
                    for p in self.constraints['partitions']:
                        for index, q_string in enumerate(queries):
                            s = queries[index] + 'queue=' + p + '&'
                            new_list.append(s)
                    queries = new_list

                if self.constraints['accounts']:
                    new_list = []
                    for a in self.constraints['accounts']:
                        for index, q_string in enumerate(queries):
                            s = queries[index] + 'repo=' + a + '&'
                            new_list.append(s)
                    queries = new_list

                for q in queries:
                    query = q.rstrip("&")
                    if query == "?" : query = ""
                    self.logger.info("sending query {} to the newt function for system {}".format(query,m))
                    try:
                        values = self.newt.get_queue(m,query)
                        if values:
                            self.raw_results.extend(values)
                    except Exception as e:
                        self.logger.error(e)
                        pass 

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
