#!/usr/bin/env python
"""
Calculates price / preformance and figure of merit and
saves it into the output file acording to design document.

"""
from __future__ import division
import pandas as pd
import numpy as np
import pprint
import sys

from decisionengine.framework.modules import Transform
from decisionengine_modules.util.figure_of_merit import figure_of_merit
import decisionengine.framework.modules.de_logger as de_logger

"""
IMPORTANT: Please do not change order of these keys and always
           append new keys rather than pre-pend or insert.
"""

CONSUMES = ["GCE_Instance_Performance",
            "Factory_Entries_GCE",
            "GCE_Occupancy" ]

PRODUCES = ["GCE_Price_Performance", "GCE_Figure_Of_Merit"]


class GceFigureOfMerit(Transform.Transform):
    def __init__(self, config):
        super(GceFigureOfMerit, self).__init__(config)
        self.logger = de_logger.get_logger()

    def transform(self, data_block):

        performance = data_block[CONSUMES[0]]
        performance["PricePerformance"] = np.where(performance["PerfTtbarTotal"] > 0,
                                                   performance["OnDemandPrice"] / performance["PerfTtbarTotal"],
                                                   sys.float_info.max)

        factory_entries = data_block[CONSUMES[1]].fillna(0)

        gce_occupancy = data_block[CONSUMES[2]].fillna(0)

        figures_of_merit = []

        for i, row in performance.iterrows():
            az = row["AvailabilityZone"]
            it = row["InstanceType"]
            entry_name = row["EntryName"]

            occupancy_df = gce_occupancy[(gce_occupancy.AvailabilityZone == az) &
                                         (gce_occupancy.InstanceType == it)]
            occupancy = float(occupancy_df["Occupancy"].values[0]) if not occupancy_df.empty else 0

            max_allowed = max_idle = idle = 0

            if (not factory_entries.empty) and ('EntryName' in factory_entries):
                factory_df = factory_entries[factory_entries.EntryName == entry_name]
                if not factory_df.empty:
                    max_allowed = float(factory_df["GlideinConfigPerEntryMaxGlideins"].values[0])
                    max_idle = float(factory_df["GlideinConfigPerEntryMaxIdle"].values[0])
                    idle = float(factory_df["GlideinMonitorTotalStatusIdle"].values[0])

            fom = figure_of_merit(row["PricePerformance"],
                                  occupancy,
                                  max_allowed,
                                  idle,
                                  max_idle)

            figures_of_merit.append({"EntryName": entry_name,
                                     "FigureOfMerit": fom})

        return {PRODUCES[0]: performance.filter(["EntryName",
                                                 "PricePerformance"]),
                PRODUCES[1]: pd.DataFrame(figures_of_merit)}

    def consumes(self, name_list=None):
        return CONSUMES

    def produces(self, name_schema_id_list=None):
        return PRODUCES


def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {
        "GceFigureOfMerit": {
           "module":  "modules.GCE.transforms.GceFigureOfMerit",
           "name":  "GceFigureOfMerit",
           "parameters": {
           }
        }
    }

    print "Entry in channel cofiguration"
    pprint.pprint(d)
    print "where"
    print "\t name - name of the class to be instantiated by task manager"


def module_config_info():
    """
    print this module configuration information
    """

    print "consumes", CONSUMES
    print "produces", PRODUCES
    module_config_template()


def main():
    """
    Call this a a test unit or use as CLI of this module
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--configtemplate",
                        action="store_true",
                        help="prints the expected module configuration")

    parser.add_argument("--configinfo",
                        action="store_true",
                        help="prints config template along with produces and consumes info")

    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()

if __name__ == "__main__":
    main()
