"""
Calculates price / preformance and figure of merit and
saves it into the output file acording to design document.

"""
import pandas as pd
import numpy as np
import sys

from decisionengine.framework.modules import Transform
from decisionengine_modules.util.figure_of_merit import figure_of_merit


@Transform.consumes(GCE_Instance_Performance=pd.DataFrame,
                    Factory_Entries_GCE=pd.DataFrame,
                    GCE_Occupancy=pd.DataFrame)
@Transform.produces(GCE_Price_Performance=pd.DataFrame,
                    GCE_Figure_Of_Merit=pd.DataFrame)
class GceFigureOfMerit(Transform.Transform):
    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )

    def transform(self, data_block):

        self.logger.debug("in GceFigureOfMerit transform")
        performance = self.GCE_Instance_Performance(data_block)
        performance["PricePerformance"] = np.where(performance["PerfTtbarTotal"] > 0,
                                                   (performance["OnDemandPrice"] /
                                                    performance["PerfTtbarTotal"]),
                                                   sys.float_info.max)

        factory_entries = self.Factory_Entries_GCE(data_block).fillna(0)
        gce_occupancy = self.GCE_Occupancy(data_block).fillna(0)

        figures_of_merit = []

        for i, row in performance.iterrows():
            az = row["AvailabilityZone"]
            it = row["InstanceType"]
            entry_name = row["EntryName"]

            occupancy_df = gce_occupancy[((gce_occupancy.AvailabilityZone == az) &
                                          (gce_occupancy.InstanceType == it))]
            occupancy = float(
                occupancy_df["Occupancy"].values[0]) if not occupancy_df.empty else 0

            max_allowed = max_idle = idle = 0

            if (not factory_entries.empty) and ('EntryName' in factory_entries):
                factory_df = factory_entries[factory_entries.EntryName == entry_name]
                if not factory_df.empty:
                    max_allowed = float(
                        factory_df["GlideinConfigPerEntryMaxGlideins"].values[0])
                    max_idle = float(
                        factory_df["GlideinConfigPerEntryMaxIdle"].values[0])
                    idle = float(
                        factory_df["GlideinMonitorTotalStatusIdle"].values[0])

            fom = figure_of_merit(row["PricePerformance"],
                                  occupancy,
                                  max_allowed,
                                  idle,
                                  max_idle)

            figures_of_merit.append({"EntryName": entry_name,
                                     "FigureOfMerit": fom})

        return {'GCE_Price_Performance': performance.filter(["EntryName",
                                                             "PricePerformance"]),
                'GCE_Figure_Of_Merit': pd.DataFrame(figures_of_merit)}


Transform.describe(GceFigureOfMerit)
