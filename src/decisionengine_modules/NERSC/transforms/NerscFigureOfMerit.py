"""
Calculates price / preformance and figure of merit and
saves it into the output file acording to design document.

"""
import sys

import numpy as np
import pandas as pd

from decisionengine.framework.modules import Transform
from decisionengine_modules.util import figure_of_merit as fom


@Transform.consumes(Nersc_Instance_Performance=pd.DataFrame, Factory_Entries_LCF=pd.DataFrame)
@Transform.produces(Nersc_Price_Performance=pd.DataFrame, Nersc_Figure_Of_Merit=pd.DataFrame)
class NerscFigureOfMerit(Transform.Transform):
    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )

    def transform(self, data_block):
        """
        NERSC Instance performance is obtained from the following CSV:

        InstanceType,AvailabilityZone,OnDemandPrice,PerfTtbarTotal,EntryName
        haswell,cori,0.576,0.96,CMSHTPC_T3_US_NERSC_Cori
        haswell_shared,cori,0.081,0.137,CMSHTPC_T3_US_NERSC_Cori_shared
        knl,cori,0.612,0.255,CMSHTPC_T3_US_NERSC_Cori_KNL
        haswell,edison,0.432,0.658,CMSHTPC_T3_US_NERSC_Edison
        haswell_shared,edison,0.108,0.164,CMSHTPC_T3_US_NERSC,Edison_shared

        by NerscInstancePerformance

        first column is HW type, second the machine, third the \"price\"
        of what 1 hr of that resource is worth

        4th column is the cms ttbar benchmark

        price/performance is the ratio of the 3rd and 4th column

        """

        self.logger.debug("in NerscFigureOfMerit transform")
        performance = self.Nersc_Instance_Performance(data_block)
        performance["PricePerformance"] = np.where(
            performance["PerfTtbarTotal"] > 0,
            (performance["OnDemandPrice"] / performance["PerfTtbarTotal"]),
            sys.float_info.max,
        )

        factory_entries_lcf = self.Factory_Entries_LCF(data_block)

        figures_of_merit = []
        for _i, row in factory_entries_lcf.iterrows():
            entry_name = row["EntryName"]
            perf_df = performance[performance.EntryName == entry_name]

            for _j, perf_row in perf_df.iterrows():
                running = float(row["GlideinMonitorTotalStatusRunning"])
                max_allowed = float(row["GlideinConfigPerEntryMaxGlideins"])
                max_idle = float(row["GlideinConfigPerEntryMaxIdle"])
                idle = float(row["GlideinMonitorTotalStatusIdle"])
                figures_of_merit.append(
                    {
                        "EntryName": entry_name,
                        "FigureOfMerit": fom.figure_of_merit(
                            perf_row["PricePerformance"], running, max_allowed, idle, max_idle
                        ),
                    }
                )

        return {
            "Nersc_Price_Performance": performance.filter(["EntryName", "PricePerformance"]),
            "Nersc_Figure_Of_Merit": pd.DataFrame(figures_of_merit),
        }


Transform.describe(NerscFigureOfMerit)
