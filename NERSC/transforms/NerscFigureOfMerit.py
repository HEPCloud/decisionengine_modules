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
import decisionengine.framework.modules.de_logger as de_logger

"""
IMPORTANT: Please do not change order of these keys and always
           append new keys rather than pre-pend or insert.
"""
CONSUMES = ["Nersc_Instance_Performance", "Factory_Entries_LCF"]

PRODUCES = ["Nersc_Price_Performance", "Nersc_Figure_Of_Merit"]


class NerscFigureOfMerit(Transform.Transform):
    def __init__(self, config):
        super(NerscFigureOfMerit, self).__init__(config)
        self.logger = de_logger.get_logger()

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

        performance = data_block[CONSUMES[0]]
        performance["PricePerformance"] = np.where(performance["PerfTtbarTotal"] > 0,
                                                   performance["OnDemandPrice"] / performance["PerfTtbarTotal"],
                                                   sys.float_info.max)

        factory_entries_lcf = data_block[CONSUMES[1]]

        figures_of_merit = []
        for i, row in factory_entries_lcf.iterrows():
            entry_name = row["EntryName"]
            perf_df = performance[performance.EntryName == entry_name]

            for j, perf_row in perf_df.iterrows():
                running = float(row["GlideinMonitorTotalStatusRunning"])
                max_allowed = float(row["GlideinConfigPerEntryMaxGlideins"])
                fom = perf_row["PricePerformance"] * (running + 1.) / max_allowed \
                    if max_allowed > 0 else sys.float_info.max

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
        "NerscFigureOfMerit": {
           "module":  "modules.NERSC.transforms.NerscFigureOfMerit",
           "name":  "NerscFigureOfMerit",
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
