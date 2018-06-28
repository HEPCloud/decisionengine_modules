"""
Get job info from Nersc
"""
import argparse
import pprint

import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine_modules.NERSC.util import newt
import decisionengine.framework.modules.de_logger as de_logger

PRODUCES = ['Nersc_Job_Info']

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

        self.raw_results = []

        # default, query edison and cori
        self.constraints['machines'] = self.constraints.get('machines',
                                                            ['edison', 'cori'])

        # get all systems that are up

        up_machines = filter(lambda x: x['status'] == 'up', self.newt.get_status())

        if not up_machines:
            self.logger.info("All machines at NERSC are down")
            return

        # filter machines that are up

        machines = filter(lambda x: x in [ y["system"] for y in up_machines],
                          self.constraints.get('machines'))
        if not machines:
            self.logger.info("All requested machines at NERSC are down")
            return

        # filter results based on constraints specified in newt_keys dictionary

        newt_keys = self.constraints.get("newt_keys",{})

        for m in machines:
            values = self.newt.get_queue(m)
            for k, v in newt_keys.iteritems():
                if v:
                    values = filter(lambda x: x[k] in v, values)
            if values:
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
            'parameters' : { 'passwd_file' : '/path/to/password_file',
                             'constraints' : {
                                 'machines': ["edison", "cori"],
                                 'newt_keys' : {
                                     'user': ["user1", "user2"],
                                     'repo': ['m2612','m2696'],
                                     'features': ["knl&quad&cache",]
                                 }
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
