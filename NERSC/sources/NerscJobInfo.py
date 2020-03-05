"""
Get job info from Nersc
"""
import argparse
import pprint
import pandas as pd
import time

from decisionengine.framework.modules import Source
from decisionengine_modules.NERSC.util import newt
import logging

PRODUCES = ['Nersc_Job_Info']

_MAX_RETRIES = 10
_RETRY_TIMEOUT = 10


class NerscJobInfo(Source.Source):
    """
    Information of jobs on NERSC machines
    """

    def __init__(self, config):
        super(NerscJobInfo, self).__init__(config)
        self.constraints = config.get('constraints')
        if not isinstance(self.constraints, dict):
            raise RuntimeError('constraints should be a dict')
        self.newt = newt.Newt(config.get('passwd_file'))
        self.logger = logging.getLogger()
        self.max_retries = config.get("max_retries", _MAX_RETRIES)
        self.retry_timeout = config.get("retry_timeout", _RETRY_TIMEOUT)

    def _acquire(self):
        """
        Helper method that does heavy lifting. 
        Called from acquire 
        :return: `dict`
        """
        raw_results = []
        # By default, query edison and cori
        self.constraints['machines'] = self.constraints.get('machines',
                                                            ['edison', 'cori'])
        # get all systems that are up
        up_machines = [x for x in self.newt.get_status() if x['status'] == 'up']
        if not up_machines:
            self.logger.info("All machines at NERSC are down")
        # filter machines that are up
        machines = [x for x in self.constraints.get('machines') if x in [y["system"] for y in up_machines]]
        if not machines:
            self.logger.info("All requested machines at NERSC are down")
        # filter results based on constraints specified in newt_keys dictionary
        newt_keys = self.constraints.get("newt_keys", {})
        for m in machines:
            values = self.newt.get_queue(m)
            for k, v in newt_keys.tems():
                if v:
                    values = [x for x in values if x[k] in v]
            if values:
                raw_results.extend(values)
        pandas_frame = pd.DataFrame(raw_results)
        return {PRODUCES[0]: pandas_frame}

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
        Acquire NERSC job info and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """
        tries = 0
        while True:
            try:
                return self._acquire()
            except RuntimeError:
                raise
            except Exception as e:
                if tries < self.max_retries:
                    tries += 1
                    time.sleep(self.retry_timeout)
                    continue
                else:
                    raise RuntimeError(str(e))


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'nersc_job_info': {
            'module': 'decisionengine_modules.NERSC.sources.NerscJobInfo',
            'name': 'NerscJobInfo',
            'parameters': {
                'passwd_file': '/path/to/password_file',
                'max_retries': 10,
                'retry_timeout': 10,
                'constraints': {
                    'machines': ["edison", "cori"],
                    'newt_keys': {
                    'user': ["user1", "user2"],
                    'repo': ['m2612', 'm2696'],
                    'features': ["knl&quad&cache", ]
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
    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == '__main__':
    main()
