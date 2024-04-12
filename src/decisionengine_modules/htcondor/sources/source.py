import abc
import traceback

# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0
from collections import defaultdict

import pandas

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine.framework.util.metrics import Gauge, Histogram
from decisionengine_modules.htcondor import htcondor_query

DEM_HTCONDOR_SLOTS_STATUS_COUNT = Gauge(
    "dem_htcondor_slots_status_count", "Number of glideins available for the client based on status.", ["source_status"]
)
DEM_HTCONDOR_CORES_COUNT = Gauge("dem_htcondor_cores_count", "Number of active cores", ["state"])
DEM_HTCONDOR_CORES_HISTOGRAM = Histogram("dem_htcondor_cores_histogram", "Histogram of active cores", ["state"])
DEM_HTCONDOR_MEMORY_COUNT = Gauge("dem_htcondor_memory_count", "Amount of memory used", ["state"])
DEM_HTCONDOR_MEMORY_HISTOGRAM = Histogram(
    "dem_htcondor_memory_histogram",
    "Histogram of memory used",
    ["state"],
    buckets=(
        1.0,
        10.0,
        100.0,
        1000.0,
        2500.0,
        5000.0,
        10000.0,
        15000.0,
        20000.0,
        30000.0,
        50000.0,
        75000.0,
        100000.0,
        250000.0,
        500000.0,
    ),
)


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
                subsystem_name=self.subsystem_name,
                pool_name=self.collector_host,
                group_attr=self.group_attr,
                logger=self.logger,
            )

            condor_status.load(self.constraint, self.classad_attrs, self.condor_config)
            source_statuses = defaultdict(int)
            for eachDict in condor_status.stored_data:
                for key, value in self.correction_map.items():
                    if eachDict.get(key) is None:
                        eachDict[key] = value
                source_statuses[eachDict["Activity"]] += 1

            for key, value in source_statuses.items():
                DEM_HTCONDOR_SLOTS_STATUS_COUNT.labels(source_status=key).set(value)

            dataframe = pandas.DataFrame(condor_status.stored_data)
            if not dataframe.empty:
                cpus_dict = defaultdict(int)
                memory_dict = defaultdict(int)
                for i in range(len(dataframe["Cpus"])):
                    cpus_dict[dataframe["State"][i]] += dataframe["Cpus"][i]
                    memory_dict[dataframe["State"][i]] += dataframe["Memory"][i]
                for key, value in cpus_dict.items():
                    DEM_HTCONDOR_CORES_COUNT.labels(state=key).set(value)
                    DEM_HTCONDOR_CORES_HISTOGRAM.labels(state=key).observe(value)
                for key, value in memory_dict.items():
                    DEM_HTCONDOR_MEMORY_COUNT.labels(state=key).set(value)
                    DEM_HTCONDOR_MEMORY_HISTOGRAM.labels(state=key).observe(value)
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

    def get_metric_values(self):
        """
        Collect and return the current values of Prometheus metrics.
        :rtype: dict
        """

        metric_values = {"slots_status_count": {}, "cores_count": {}, "memory_count": {}}

        metrics = {
            "slots_status_count": DEM_HTCONDOR_SLOTS_STATUS_COUNT,
            "cores_count": DEM_HTCONDOR_CORES_COUNT,
            "memory_count": DEM_HTCONDOR_MEMORY_COUNT,
        }

        for metric_name, metric in metrics.items():
            for sample in metric.collect():
                for sample in sample.samples:
                    labels = sample.labels
                    status = labels.get("source_status" if metric_name == "slots_status_count" else "state", "Unknown")
                    count = sample.value
                    metric_values[metric_name][status] = count

        return metric_values
