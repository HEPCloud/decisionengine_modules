from functools import partial
import pandas

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.util.retry_function import retry_wrapper
from decisionengine_modules.htcondor import htcondor_query

@Source.supports_config(Parameter('condor_config', type=str, comment="path to condor configuration"),
                        Parameter('factories',
                                  default=[],
                                  comment="""Supported list entry layout:

  {
    'collector_host': 'factory_collector.com',
    'classad_attrs': [],
    'constraints': 'HTCondor classad query constraints'
  }
"""),
                        Parameter('nretries', default=0),
                        Parameter('retry_interval', default=0))
@Source.produces(Factory_Entries_Grid=pandas.DataFrame,
                 Factory_Entries_AWS=pandas.DataFrame,
                 Factory_Entries_GCE=pandas.DataFrame,
                 Factory_Entries_LCF=pandas.DataFrame)
class FactoryEntries(Source.Source):

    def __init__(self, config):
        super().__init__(config)
        self.condor_config = config.get('condor_config')
        self.factories = config.get('factories', [])
        self._entry_gridtype_map = {
            'Factory_Entries_Grid': ('gt2', 'condor'),
            'Factory_Entries_AWS': ('ec2',),
            'Factory_Entries_GCE': ('gce',),
            'Factory_Entries_LCF': ('batch slurm',)
        }

        # The combination of nretries=10 and retry_interval=2 adds up to just
        # over 15 minutes
        self.nretries = config.get('nretries', 0)
        self.retry_interval = config.get('retry_interval', 0)

        self.subsystem_name = 'any'
        self.logger = self.logger.bind(module=__name__.split(".")[-1])

    def acquire(self):
        """
        Acquire factory entries from the factory collector
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        self.get_logger().debug("in FactoryEntries::acquire()")
        dataframe = pandas.DataFrame()

        for factory in self.factories:
            collector_host = factory.get('collector_host')
            constraint = '(%s)&&(glideinmytype=="glidefactory")' % \
                factory.get('constraint', True)
            classad_attrs = factory.get('classad_attrs')
            correction_map = factory.get('correction_map')

            try:
                condor_status = htcondor_query.CondorStatus(
                    subsystem_name=self.subsystem_name,
                    pool_name=collector_host,
                    group_attr=['GLIDEIN_GridType'])

                retry_wrapper(
                    partial(condor_status.load,
                            *(constraint, classad_attrs, self.condor_config)),
                    self.get_logger(),
                    nretries=self.nretries,
                    retry_interval=self.retry_interval)

                if correction_map is not None:
                    for eachDict in condor_status.stored_data:
                        for key, value in correction_map.items():
                            if eachDict.get(key) is None:
                                eachDict[key] = value

                df = pandas.DataFrame(condor_status.stored_data)
                if not df.empty:
                    (col_host, sec_cols) = htcondor_query.split_collector_host(
                        collector_host)
                    df['CollectorHost'] = [col_host] * len(df)
                    if sec_cols != '':
                        df['CollectorHosts'] = ['%s,%s' %
                                                (col_host, sec_cols)] * len(df)
                    else:
                        df['CollectorHosts'] = [col_host] * len(df)

                    dataframe = pandas.concat([dataframe, df],
                                              ignore_index=True, sort=True)
            except htcondor_query.QueryError:
                self.get_logger().exception(f"Failed to fetch glidefactory classads from collector host(s) {collector_host}")
            except Exception:
                self.get_logger().exception(f"Unexpected error fetching glidefactory classads from collector host(s) {collector_host}")

        if dataframe.empty:
            # There were no entry classads in the factory collector or
            # quering the collector failed
            return dict.fromkeys(self._entry_gridtype_map, pandas.DataFrame())

        results = {}
        for key, value in self._entry_gridtype_map.items():
            results[key] = dataframe.loc[(dataframe.GLIDEIN_GridType.isin(list(value)))]
        return results


Source.describe(FactoryEntries)
