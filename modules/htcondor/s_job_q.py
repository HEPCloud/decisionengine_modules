#!/usr/bin/python
import argparse
import pprint
import pandas
import numpy

from decisionengine.framework.modules import Source
from decisionengine.modules.htcondor import htcondor_query


PRODUCES = ['job_manifests']


class JobQ(Source.Source):

    def __init__ (self, *args, **kwargs):
        if args:
            config = args[0]
        else:
            config = {}

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')
        self.collector_host = config.get('collector_host')
        self.schedds = config.get('schedds', [None])
        self.condor_config = config.get('condor_config')
        self.constraint = config.get('constraint', True)
        self.classad_attrs = config.get('classad_attrs')


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def acquire(self):
        """
        Acquire jobs from the HTCondor Schedd
        :rtype: :obj:`~pd.DataFrame`
        """

        dataframe = pandas.DataFrame()
        for schedd in self.schedds:
            condor_q = htcondor_query.CondorQ(schedd_name=schedd,
                                              pool_name=self.collector_host)
            condor_q.load(constraint=self.constraint,
                          format_list=self.classad_attrs,
                          condor_config=self.condor_config)
            jobs = []
            for job in condor_q.stored_data:
                jobs.extend(job)
            df = pandas.DataFrame(condor_q.stored_data)
            # Add schedd name to the jobs
            df['ScheddName'] = pandas.Series([schedd]*len(condor_q.stored_data))
            df['CollectorHost'] = pandas.Series([self.collector_host]*len(condor_q.stored_data))
            dataframe = dataframe.append(df, ignore_index=True)
        return {'job_manifests': dataframe}


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'job_manifests': {
            'module': 'modules.htcondor.s_job_q',
            'name': 'JobQ',
            'parameters': {
                'collector_host': 'factory_collector.com',
                'schedds': ['job_schedd1', 'job_schedd2'],
                'condor_config': '/path/to/condor_config',
                'constraints': 'HTCondor job query constraints',
                'classad_attrs': '[]',
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

