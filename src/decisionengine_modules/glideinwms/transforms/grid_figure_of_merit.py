# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas

from decisionengine.framework.modules import Transform
from decisionengine.framework.modules.Transform import Parameter
from decisionengine_modules.util.figure_of_merit import figure_of_merit, FIGURE_OF_MERIT_CALCULATION

ATTR_ENTRYNAME = "EntryName"
ATTR_FOM = "Grid_Figure_Of_Merit"


@Transform.supports_config(Parameter("price_performance", default=1))
@Transform.consumes(Factory_Entries=pandas.DataFrame)
@Transform.produces(Grid_Figure_Of_Merit=pandas.DataFrame)
class GridFigureOfMerit(Transform.Transform):
    def __init__(self, config):
        super().__init__(config)
        self.price_performance = config.get("price_performance", 1)

    def transform(self, datablock):
        """
        Grid sites FOM are straight up assumed as 0 for now
        """

        self.logger.debug("in GridFigureOfMerit transform")
        entries = pandas.DataFrame([])
        if "Grid" in self.Factory_Entries(datablock).index:
            entries = self.Factory_Entries(datablock).xs("Grid")
        if entries is None:
            entries = pandas.DataFrame({ATTR_ENTRYNAME: []})
        foms = []
        if not entries.empty:
            for _index, entry in entries.iterrows():
                running = float(entry["GlideinMonitorTotalStatusRunning"])
                max_allowed = float(entry["GlideinConfigPerEntryMaxGlideins"])
                max_idle = float(entry["GlideinConfigPerEntryMaxIdle"])
                idle = float(entry["GlideinMonitorTotalStatusIdle"])

                # Instrumentation
                fom_value = figure_of_merit(self.price_performance, running, max_allowed, idle, max_idle, self.logger)
                f = {ATTR_ENTRYNAME: entry[ATTR_ENTRYNAME], ATTR_FOM: fom_value}
                foms.append(f)

                #FOM Metric
                FIGURE_OF_MERIT_CALCULATION.labels(
                    performance=self.price_performance,
                    running=running,
                    max_allowed=max_allowed,
                    idle=idle,
                    max_idle=max_idle
                ).set(fom_value)

        return {"Grid_Figure_Of_Merit": pandas.DataFrame(foms)}


Transform.describe(GridFigureOfMerit)
