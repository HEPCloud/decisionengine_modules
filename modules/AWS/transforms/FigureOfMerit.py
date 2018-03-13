#!/usr/bin/env python
"""
Calculates price / preformance and figure of merit and
saves it into the output file acording to design document.

"""
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
          'Job_Limits', 'AWS_Occupancy']

PRODUCES=['AWS_Price_Performance',
          'AWS_Figure_Of_Merit']

DEFAULT_MAX_LIMIT=20

def price_performance(SpotPrice, PerfTtbarTotal):
    pp = 0.
    if PerfTtbarTotal > 0.:
        pp = (float(SpotPrice) / float(PerfTtbarTotal))
    return pp

def figure_of_merit(RunningVms, MaxLimit, PricePerf):
    if int(MaxLimit) > 0:
        return ((float(RunningVms)+1) / int(MaxLimit)) * PricePerf
    else:
        return 0.

class FOMEntry(object):
    def __init__(self, fe_data):
        """
        :type fe_data: :obj:`dict`
        :arg fe_data: factory entry data element
        """
        self.data = fe_data
    
    def __cmp__(self, other = None):
        """
        overrides comparison method
        """
        rc = -1
        try:
             if (self.data['AvailabilityZone'], self.data['InstanceType'], self.data['AccountName']) \
                == (other.data['AvailabilityZone'], other.data['InstanceType'], other.data['AccountName']):
                rc = 0
        except:
            pass
        return rc

    def __repr__(self):
        return '%s'%(self.data,)

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

        fom_data = []
        spot_prices = data_block.get('provisioner_resource_spot_prices').to_dict(orient='records')
        perf_data = data_block.get('Performance_Data').to_dict(orient='records')
        occup_data = data_block.get('AWS_Occupancy').to_dict(orient='records')
        jl_data = data_block.get('Job_Limits').to_dict(orient='records')

        for e in spot_prices:
            data = dict(map(lambda k: (k, e.get(k)), ['AccountName', 'AvailabilityZone', 'InstanceType']))
            fom_row = FOMEntry(e)
            if fom_row not in fom_data:
                fom_data.append(fom_row)
            i = fom_data.index(fom_row)
            for r in perf_data:
                if ((fom_row.data['AvailabilityZone'] and
                    fom_row.data['InstanceType']) ==
                    (r['AvailabilityZone'] and r['InstanceType'])):
                    fom_data[i].data['PerfTtbarTotal'] = r['PerfTtbarTotal']
                    break
            else:
                fom_data[i].data['PerfTtbarTotal'] = 0.
            for r in perf_data:
                if ((fom_row.data['AvailabilityZone'] and
                    fom_row.data['InstanceType']) ==
                    (r['AvailabilityZone'] and r['InstanceType'])):
                    fom_data[i].data['PerfTtbarTotal'] = r['PerfTtbarTotal']
                    break
            else:
                fom_data[i].data['PerfTtbarTotal'] = 0.

            for r in jl_data:
                if ((fom_row.data['AvailabilityZone'] and
                    fom_row.data['InstanceType']) ==
                    (r['AvailabilityZone'] and r['InstanceType'])):
                    fom_data[i].data['MaxLimit'] = r['MaxLimit']
                    break
            else:
                fom_data[i].data['MaxLimit'] = DEFAULT_MAX_LIMIT

        pp_list = []
        fom_list = []
        for e in fom_data:
            perf_ttbar_total = e.data['PerfTtbarTotal'] if 'PerfTtbarTotal' in e.data else 0
            pp = copy.copy(e.data)
            fom = copy.copy(e.data)
            pp['AWS_Price_Performance'] = price_performance(e.data['SpotPrice'],
                                                            perf_ttbar_total)
            running_vms = e.data['RunningVms'] if 'RunningVms' in e.data else 0
            max_limit = e.data['MaxLimit'] if 'MaxLimit' in e.data else DEFAULT_MAX_LIMIT
            fom['AWS_Figure_Of_Merit'] = figure_of_merit(running_vms,
                                                         max_limit,
                                                         pp['AWS_Price_Performance'])
            pp_list.append(pp)
            fom_list.append(fom)
        
        return {PRODUCES[0]: pd.DataFrame(pp_list), PRODUCES[1]:pd.DataFrame(fom_list)}

    def consumes(self):
        return CONSUMES

    def produces(self):
        return PRODUCES

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"FigureOfMerit": {
        "module":  "modules.AWS.transforms.FigureOfMerit",
        "name":  "FigureOfMerit",
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

        data_block = datablock.DataBlock(ds,
                                         '6D596F43-B4DB-4418-812A-79869001E72B',
                                         1)

        fm_info = FigureOfMerit()
        rc = fm_info.transform(data_block)
        print "INFO"
        print rc

if __name__ == '__main__':
    main()
