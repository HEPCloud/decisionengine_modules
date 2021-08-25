import pandas
import traceback

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.htcondor import htcondor_query


@Source.supports_config(Parameter('collector_host', type=str),
                        Parameter('schedds', default=[None]),
                        Parameter('condor_config', type=str),
                        Parameter('constraint', default=True),
                        Parameter('classad_attrs', type=list),
                        Parameter('correction_map', type=dict))
@Source.produces(job_manifests=pandas.DataFrame)
class JobQ(Source.Source):

    def __init__(self, config):
        """
        In config files such as job_classification.jsonnet or Nersc.jsonnet,
        put a dictionary named correction_map with keys corresponding to classad_attrs
        and values that the operators want to be default values for the classad_attrs.
        """
        super().__init__(config)

        self.collector_host = config.get('collector_host')
        self.schedds = config.get('schedds', [None])
        self.condor_config = config.get('condor_config')
        self.constraint = config.get('constraint', True)
        self.classad_attrs = config.get('classad_attrs')
        self.logger = self.logger.bind(module=__name__.split(".")[-1])
        self.correction_map = config.get('correction_map')

    def acquire(self):
        """
        Acquire jobs from the HTCondor Schedd
        :rtype: :obj:`~pd.DataFrame`
        """
        self.get_logger().debug("in htcondor JobQ::acquire")

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
                self.get_logger().warning('Query error fetching job classads from schedd "%s" in collector host(s) "%s".' %
                                          (schedd, collector_host))
            except Exception:
                msg = 'Unexpected error fetching job classads from schedd "{}" in collector host(s) "{}".'
                self.get_logger().warning(msg.format(schedd, collector_host))
                self.get_logger().error(msg.format(
                    schedd, collector_host) + " Traceback: {}".format(traceback.format_exc()))
        return {'job_manifests': dataframe}


Source.describe(JobQ)
