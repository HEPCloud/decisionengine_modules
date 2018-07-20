#!/usr/bin/env python
"""
Calculates price / preformance and figure of merit and
saves it into the output file acording to design document.

"""
from __future__ import division
import pandas as pd
import numpy as np
import pprint
import re
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
        self.config = config
        self.logger = de_logger.get_logger()

    def transform(self, data_block):
        """
        NERS Instance performance is obtained from the following CSV:

        InstanceType,AvailabilityZone,OnDemandPrice,PerfTtbarTotal
        haswell,cori,0.576,0.96
        haswell_shared,cori,0.081,0.137
        knl,cori,0.612,0.255
        haswell,edison,0.432,0.658

        by NerscInstancePerformance

        first column is HW type, second the machine, third the \"price\" 
        of what 1 hr of that resource is worth 

        4th column is the cms ttbar benchmark 

        So therefore price/performance is the ratio of the 3rd and 4th column

        Factory_Entries_LCF data frame contains EntryName column 
        which is defined in the following way:

        EntryName=${VO_PREFIX}_${SITE_PREFIX}_${Avalability_Zone}_${Instance_Type}
        
        VO_PREFIX = ['CMSHTPC', 'FIFE']
        SITE_PREFIX = T3_US_NERSC
        Avalability_Zone = ['Cori', 'Edison'] (matches AvailabilityZone from Nersc_Instance_Performance)
        Instance_Type = ['KNL','Edison'] (matches InstanceType from Nersc_Instance_Performance)

        Above mapping is captured in configuration of this 
        modulde under "entry_name_mapping" key
        
        user mapping (for the future):

        hufnagel-> cms   timm-> mu2e  burt -> nova 

        mapping: 

         InstanceType,AvailabilityZone        EntryName
         haswell,cori                         CMSHTPC_T3_US_NERSC_Cori
         haswell_shared,cori                  CMSHTPC_T3_US_NERSC_Cori_shared
         knl,cori,0.612,0.255                 CMSHTPC_T3_US_NERSC_Cori_KNL
         haswell,edison,0.432,0.658           CMSHTPC_T3_US_NERSC_Edison
         
         For FIFE substitute FIFE for CMSHTPC above
        """

        performance = data_block[CONSUMES[0]]
        performance["PricePerformance"] = np.where(performance["PerfTtbarTotal"] > 0,
                                                   performance["OnDemandPrice"] / performance["PerfTtbarTotal"],
                                                   sys.float_info.max)

        factory_entries_lcf = data_block[CONSUMES[1]]

        try:
            entry_name_mapping = self.config["entry_name_mapping"]
        except KeyError:
            raise RuntimeError("Transform {} is misconfigured. Configuration is missing \"entry_name_mapping\" key.".
                                   format(self.__class__.__name__))

        figures_of_merit = []
        for i, row in factory_entries_lcf.iterrows():
            entry_name = row["EntryName"]
            key = re.sub("^[^_]*_", "", entry_name)
            try:
                instance_type, availability_zone = entry_name_mapping.get(key).split(",")
            except AttributeError:
                raise RuntimeError("Transform {} is misconfigured. Configuration \"entry_name_mapping\" is missing key = {}.".
                                   format(self.__class__.__name__, key))
            perf_df = performance[(performance.InstanceType == instance_type) &
                                  (performance.AvailabilityZone == availability_zone)]

            for j, perf_row in perf_df.iterrows():
                running = float(row["GlideinMonitorTotalStatusRunning"])
                max_allowed = float(row["GlideinConfigPerEntryMaxGlideins"])
                fom = perf_row["PricePerformance"] * running / max_allowed if max_allowed > 0 else sys.float_info.max

                figures_of_merit.append({"EntryName": entry_name,
                                         "FigureOfMerit": fom})

        return {PRODUCES[0]: performance.filter(["InstanceType",
                                                 "AvailabilityZone",
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
           "module":  "modules.AWS.transforms.NerscFigureOfMerit",
           "name":  "NerscFigureOfMerit",
           "parameters": {
               "entry_name_mapping" : { 
                   "T3_US_NERSC_Cori" : "haswell,cori",
                   "T3_US_NERSC_Cori_shared" : "haswell_shared,cori", 
                   "T3_US_NERSC_Cori_KNL" : "knl,cori",
                   "T3_US_NERSC_Edison" : "haswell,edison",
               },
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
