import argparse
import logging
import pandas
import pprint
import traceback

from decisionengine.framework.modules import Source
from decisionengine_modules.htcondor import htcondor_query

PRODUCES = ['job_manifests']


class JobQ(Source.Source):

    def __init__(self, config):
        """
        In config files such as job_classification.jsonnet or Nersc.jsonnet,
        put a dictionary named correction_map with keys corresponding to classad_attrs
        and values that the operators want to be default values for the classad_attrs.
        """
        super(JobQ, self).__init__(config)

        if not self.parameters:
            self.parameters = {}
        if not isinstance(self.parameters, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.collector_host = self.parameters.get('collector_host')
        self.schedds = self.parameters.get('schedds', [None])
        self.condor_config = self.parameters.get('condor_config')
        self.constraint = self.parameters.get('constraint', True)
        self.classad_attrs = self.parameters.get('classad_attrs')
        self.logger = logging.getLogger()
        self.correction_map = self.parameters.get('correction_map')

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
        (collector_host, secondary_collectors) = htcondor_query.split_collector_host(
            self.collector_host)
        for schedd in self.schedds:
            try:
                condor_q = htcondor_query.CondorQ(schedd_name=schedd,
                                                  pool_name=self.collector_host)
                condor_q.load(constraint=self.constraint,
                              format_list=self.classad_attrs,
                              condor_config=self.condor_config)

                for eachDict in condor_q.stored_data:
                    for key, value in self.correction_map.items():
                        if eachDict.get(key) is None:
                            eachDict[key] = value

                df = pandas.DataFrame(condor_q.stored_data)
                if not df.empty:
                    # Add schedd name and collector host to job records
                    df['ScheddName'] = pandas.Series(
                        [schedd] * len(condor_q.stored_data))
                    df['CollectorHost'] = pandas.Series(
                        [collector_host] * len(condor_q.stored_data))
                    dataframe = dataframe.append(df, ignore_index=True)
            except htcondor_query.QueryError:
                self.logger.warning('Query error fetching job classads from schedd "%s" in collector host(s) "%s".' %
                                    (schedd, collector_host))
            except Exception:
                msg = 'Unexpected error fetching job classads from schedd "{}" in collector host(s) "{}".'
                self.logger.warning(msg.format(schedd, collector_host))
                self.logger.error(msg.format(
                    schedd, collector_host) + " Traceback: {}".format(traceback.format_exc()))
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
