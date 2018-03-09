#!/usr/bin/env python
"""
Calculates price / preformance and figure of merit and
saves it into the output file acording to design document.

"""
from __future__ import division
import os
import copy
import pprint
import pandas as pd

from decisionengine.framework.modules import Transform
import decisionengine.framework.configmanager.ConfigManager as configmanager
import decisionengine.framework.dataspace.datablock as datablock
import decisionengine.framework.dataspace.dataspace as dataspace

CONSUMES=['provisioner_resource_spot_prices',
          'Performance_Data',
          'Job_Limits', 'AWS_Occupancy'
          ]

PRODUCES=['AWS_Price_Performance',
          'AWS_Figure_Of_Merit']

DEFAULT_MAX_LIMIT=20

def price_performance(SpotPrice, PerfTtbarTotal):
    pp = 0.
    if float(PerfTtbarTotal) > 0.:
        pp = (float(SpotPrice) / float(PerfTtbarTotal))
    return pp

def figure_of_merit(RunningVms, MaxLimit, PricePerf):
    fm = 0.
    if int(MaxLimit) > 0:
        fm = ((float(RunningVms)+1) / int(MaxLimit)) * PricePerf
    return fm

class FigureOfMerit(Transform.Transform):
    def __init__(self, *args, **kwargs):
        pass
        # super(FigureOfMerit, self).__init__()

    def transform(self, data_block):
        """
        Make all necessary calculations

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block

        :rtype: pandas frame (:class:`pd.DataFramelist`)
        """

        spot_price_data = data_block.get('provisioner_resource_spot_prices')
        perf_data = data_block.get('Performance_Data')
        occup_data = data_block.get('AWS_Occupancy')
        job_limits_data = data_block.get('Job_Limits')

        price_perf_rows = []
        fom_rows = []
        for i, row in spot_price_data.iterrows():
           if perf_data.empty:
               r1 = perf_data
           else:
               r1 = perf_data.loc[(perf_data['AvailabilityZone'] == row['AvailabilityZone']) & (perf_data['InstanceType'] == row['InstanceType'])]

           if occup_data.empty:
               r2 = occup_data
           else:
               r2 = occup_data[(occup_data['AvailabilityZone'] == row['AvailabilityZone']) & (occup_data['InstanceType'] == row['InstanceType'])]

           if job_limits_data.empty:
               r3 = job_limits_data
           else:
               r3 = job_limits_data[(job_limits_data.AWSProfile == row['AccountName']) & (job_limits_data['AvailabilityZone'] == row['AvailabilityZone']) & (job_limits_data['InstanceType'] == row['InstanceType'])]

           price_perf_row = copy.copy(row)
           fom_row = copy.copy(row)

           if r1.empty:
               price_perf_row['PerfTtbarTotal'] = 0.
               fom_row['PerfTtbarTotal'] = 0.
           else:
               price_perf_row['PerfTtbarTotal'] = r1['PerfTtbarTotal'].values[0]
               fom_row['PerfTtbarTotal'] = r1['PerfTtbarTotal'].values[0]
        
           if r2.empty:
               running_vms = 0
           else:
               running_vms = r2['RunningVms'].values[0]

           if r3.empty:
               price_perf_row['MaxLimit'] = DEFAULT_MAX_LIMIT
               fom_row['MaxLimit'] = DEFAULT_MAX_LIMIT
           else:
               price_perf_row['MaxLimit'] = r3['MaxLimit'].values[0]
               fom_row['MaxLimit'] = r3['MaxLimit'].values[0]
           
           price_perf = price_performance(row['SpotPrice'],
                                          price_perf_row['PerfTtbarTotal'])
           price_perf_row['AWS_Price_Performance'] = price_perf
           fom_row['AWS_Figure_Of_Merit'] = figure_of_merit(running_vms,
                                                        price_perf_row['MaxLimit'],
                                                        price_perf)
           price_perf_rows.append(price_perf_row)
           fom_rows.append(fom_row)
            
        price_perf_df = pd.DataFrame(price_perf_rows)
        price_perf_df.reindex_axis(sorted(price_perf_df.columns), axis=1)
        fom_df = pd.DataFrame(fom_rows)
        fom_df.reindex_axis(sorted(fom_df.columns), axis=1)
        return {PRODUCES[0]: price_perf_df, PRODUCES[1]:fom_df}
            
    def consumes(self):
        return CONSUMES

    def produces(self):
        return PRODUCES

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"FigureOfMerit": {
        "module" :  "modules.AWS.transforms.FigureOfMerit",
        "name"   :  "FigureOfMerit",
        },
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

    parser.add_argument('--configtemplate',
                        action='store_true',
                        help='prints the expected module configuration')

    parser.add_argument('--configinfo',
                        action='store_true',
                        help='prints config template along with produces and consumes info')
    args = parser.parse_args()
    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        config_manager = configmanager.ConfigManager()
        config_manager.load()
        global_config = config_manager.get_global_config()
        print "GLOBAL CONF", global_config
        ds = dataspace.DataSpace(global_config)

        #data_block = datablock.DataBlock(ds,
        #                                 '6D596F43-B4DB-4418-812A-79869001E72B',
        #                                 1)
        data_block = datablock.DataBlock(ds,
                                         "AWS_Calculations",
                                         "B183F454-5E7D-45B3-B4D2-E3D26392578B",
                                         1,
                                         151)

        fm_info = FigureOfMerit()
        rc = fm_info.transform(data_block)
        print "INFO"
        print rc

if __name__ == '__main__':
    main()
