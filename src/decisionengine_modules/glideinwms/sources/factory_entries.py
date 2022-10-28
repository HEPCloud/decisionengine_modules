# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from functools import partial

import pandas

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.util.retry_function import retry_wrapper

ENTRY_TYPES = {
    "Grid": ["gt2", "condor"],
    "AWS": ["ec2"],
    "GCE": ["gce"],
    "LCF": ["batch slurm"],
}


@Source.supports_config(
    Parameter("condor_config", type=str, comment="path to condor configuration"),
    Parameter(
        "factories",
        default=[],
        comment="""Supported list entry layout:

  {
    'collector_host': 'factory_collector.com',
    'classad_attrs': [],
    'constraints': 'HTCondor classad query constraints'
  }
""",
    ),
    Parameter("max_retries", default=0),
    Parameter("retry_interval", default=0),
)
@Source.produces(Factory_Entries=pandas.DataFrame)
class FactoryEntries(Source.Source):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.condor_config = config.get("condor_config")
        self.factories = config.get("factories", [])

        # The combination of max_retries=10 and retry_interval=2 adds up to just
        # over 15 minutes
        self.max_retries = config.get("max_retries", 0)
        self.retry_interval = config.get("retry_interval", 0)

        self.subsystem_name = "any"

    def acquire(self):
        """
        Acquire factory entries from the factory collector
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        self.logger.debug("in FactoryEntries acquire")
        dataframe = pandas.DataFrame()

        for factory in self.factories:
            collector_host = factory.get("collector_host")
            constraint = f"({factory.get('constraint', True)})&&(glideinmytype==\"glidefactory\")"
            classad_attrs = factory.get("classad_attrs")
            correction_map = factory.get("correction_map")

            try:
                condor_status = htcondor_query.CondorStatus(
                    subsystem_name=self.subsystem_name,
                    pool_name=collector_host,
                    group_attr=["GLIDEIN_GridType"],
                    logger=self.logger,
                )

                retry_wrapper(
                    partial(condor_status.load, *(constraint, classad_attrs, self.condor_config)),
                    max_retries=self.max_retries,
                    retry_interval=self.retry_interval,
                    logger=self.logger,
                )

                if correction_map is not None:
                    for eachDict in condor_status.stored_data:
                        for key, value in correction_map.items():
                            if eachDict.get(key) is None:
                                eachDict[key] = value

                df = pandas.DataFrame(condor_status.stored_data)
                if not df.empty:
                    col_host, sec_cols = htcondor_query.split_collector_host(collector_host)
                    df["CollectorHost"] = col_host
                    if sec_cols != "":
                        df["CollectorHosts"] = f"{col_host},{sec_cols}"
                    else:
                        df["CollectorHosts"] = col_host

                    dataframe = pandas.concat([dataframe, df], ignore_index=True, sort=True)
            except htcondor_query.QueryError:
                self.logger.exception(f"Failed to fetch glidefactory classads from collector host(s) {collector_host}")
            except Exception:
                self.logger.exception(
                    f"Unexpected error fetching glidefactory classads from collector host(s) {collector_host}"
                )

        if dataframe.empty:
            # There were no entry classads in the factory collector or
            # quering the collector failed
            return {"Factory_Entries": pandas.DataFrame()}

        dfs = [dataframe.loc[dataframe.GLIDEIN_GridType.isin(value)] for value in ENTRY_TYPES.values()]
        return {"Factory_Entries": pandas.concat(dfs, keys=ENTRY_TYPES.keys())}


Source.describe(FactoryEntries)
