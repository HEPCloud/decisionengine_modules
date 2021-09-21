import abc
import traceback

import pandas

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.htcondor import htcondor_query


@Source.supports_config(
    Parameter("collector_host", type=str),
    Parameter("condor_config", type=str),
    Parameter("constraint", default=True),
    Parameter("classad_attrs", type=list),
    Parameter("group_attr", default=["Name"]),
    Parameter("subsystem_name", type=str),
    Parameter("correction_map", default={}),
)
class ResourceManifests(Source.Source, metaclass=abc.ABCMeta):
    def __init__(self, config):
        """
        In config files such as job_classification.jsonnet or Nersc.jsonnet,
        put a dictionary named correction_map with keys corresponding to classad_attrs
        and values that the operators want to be default values for the classad_attrs.
        But here, we make available the option of an empty dictionary
        because some classes that extend this class might not have correction_map
        avaiable in its config file.
        """
        super().__init__(config)
        self.collector_host = config.get("collector_host")
        self.condor_config = config.get("condor_config")
        self.constraint = config.get("constraint", True)
        self.classad_attrs = config.get("classad_attrs")
        self.group_attr = config.get("group_attr", ["Name"])
        self.subsystem_name = config.get("subsystem_name")
        self.correction_map = self.parameters.get("correction_map", {})

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{vars(self)}"

    @abc.abstractmethod
    def acquire(self):
        """
        Acquire startd classads from the HTCondor Schedd
        :rtype: :obj:`~pd.DataFrame`
        """
        return

    def load(self):
        """
        Acquire resource classads from the HTCondor Collector
        :rtype: :obj:`~pd.DataFrame`
        """

        self.logger.debug("in ResourceManifests load")
        dataframe = pandas.DataFrame()
        try:
            condor_status = htcondor_query.CondorStatus(
                subsystem_name=self.subsystem_name, pool_name=self.collector_host, group_attr=self.group_attr
            )

            condor_status.load(self.constraint, self.classad_attrs, self.condor_config)

            for eachDict in condor_status.stored_data:
                for key, value in self.correction_map.items():
                    if eachDict.get(key) is None:
                        eachDict[key] = value

            dataframe = pandas.DataFrame(condor_status.stored_data)
            if not dataframe.empty:
                (collector_host, secondary_collectors) = htcondor_query.split_collector_host(self.collector_host)
                dataframe["CollectorHost"] = [collector_host] * len(dataframe)
                if secondary_collectors != "":
                    dataframe["CollectorHosts"] = [f"{collector_host},{secondary_collectors}"] * len(dataframe)
                else:
                    dataframe["CollectorHosts"] = [collector_host] * len(dataframe)
        except htcondor_query.QueryError:
            self.logger.warning(f'Query error fetching classads from collector host(s) "{self.collector_host}"')
            self.logger.error(
                f'Query error fetching classads from collector host(s) "{self.collector_host}". Traceback: {traceback.format_exc()}'
            )
        except Exception:
            self.logger.warning(f'Unexpected error fetching classads from collector host(s) "{self.collector_host}"')
            self.logger.error(
                f'Unexpected error fetching classads from collector host(s) "{self.collector_host,}". Traceback: {traceback.format_exc()}'
            )

        return dataframe
