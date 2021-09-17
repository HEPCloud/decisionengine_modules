from functools import partial

import pandas

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.util.retry_function import retry_wrapper


@Source.supports_config(
    Parameter("condor_config", type=str),
    Parameter(
        "factories",
        default=[],
        comment="""Supported entries are of the form:

  {
     'collector_host': 'factory_collector-2.com',
     'classad_attrs': [],
     'constraints': 'HTCondor classad query constraints'
  }
""",
    ),
    Parameter("nretries", default=0),
    Parameter("retry_interval", default=0),
)
@Source.produces(factoryglobal_manifests=pandas.DataFrame)
class FactoryGlobalManifests(Source.Source):
    def __init__(self, config):
        if not config:
            config = {}
        if not isinstance(config, dict):
            raise RuntimeError("parameters for module config should be a dict")

        super().__init__(config)
        self.condor_config = config.get("condor_config")
        self.factories = config.get("factories", [])

        # The combination of nretries=10 and retry_interval=2 adds up to just
        # over 15 minutes
        self.nretries = config.get("nretries", 0)
        self.retry_interval = config.get("retry_interval", 0)

        self.subsystem_name = "any"
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )

    def acquire(self):
        """
        Acquire factory entries from the factory collector
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        self.logger.debug("in FactoryGlobalManifests acquire")
        dataframe = None

        for factory in self.factories:
            collector_host = factory.get("collector_host")
            constraint = f"({factory.get('constraint', True)})&&(glideinmytype==\"glidefactoryglobal\")"
            classad_attrs = []

            try:
                condor_status = htcondor_query.CondorStatus(
                    subsystem_name=self.subsystem_name, pool_name=collector_host, group_attr=["Name"]
                )

                retry_wrapper(
                    partial(condor_status.load, *(constraint, classad_attrs, self.condor_config)),
                    nretries=self.nretries,
                    retry_interval=self.retry_interval,
                )

                df = pandas.DataFrame(condor_status.stored_data)
                if not df.empty:
                    (col_host, sec_cols) = htcondor_query.split_collector_host(collector_host)
                    df["CollectorHost"] = [col_host] * len(df)
                    if sec_cols != "":
                        df["CollectorHosts"] = [f"{col_host},{sec_cols}"] * len(df)
                    else:
                        df["CollectorHosts"] = [col_host] * len(df)

                    dataframe = pandas.concat([dataframe, df], ignore_index=True, sort=True)
            except htcondor_query.QueryError:
                self.logger.exception(
                    f'Failed to get glidefactoryglobal classads from collector host(s) "{collector_host}"'
                )
            except Exception:
                self.logger.exception(
                    "Unexpected error fetching "
                    "glidefactoryglobal classads from "
                    "collector host(s) "
                    f"{collector_host}"
                )

        return {"factoryglobal_manifests": dataframe}


Source.describe(FactoryGlobalManifests)
