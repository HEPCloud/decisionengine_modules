#!/usr/bin/env python
"""
Read the financial parameters from the config file and return as a dataframe
"""
import os
import pandas
import pprint

from decisionengine.framework.modules import Source

PRODUCES = ["financial_params"]

class FinancialParameters(Source.Source):
    def __init__ (self, params_dict):
        pass

    def produces(self,schema_id_list): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self,params_dict):
	financial_params=pandas.DataFrame(params_dict)
        return financial_params

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"FinancialParameters": {
        "module" :  "modules.AWS.sources.FinancialParameters",
        "name"   :  "FinancialParameters",
                    "parameters": {
                        "target_aws_vm_burn_rate":     [ 9.0 ],
                        "target_aws_bill_burn_rate":  [ 10.0 ],
                        "target_aws_balance":       [ 1000.0 ],
                        "target_gce_vm_burn_rate":   [   9.0 ],
                        "target_gce_balance":       [ 1000.0 ],
                    }
        },
        "schedule": 60*60,
    }

    print "Entry in channel configuration"
    pprint.pprint(d)
    print "where"
    print "\t params - are the desired burn rates and balances"

def module_config_info():
    """
    print this module configuration information
    """
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
        myparams= {
            "target_aws_vm_burn_rate":     [ 9.0 ],
            "target_aws_bill_burn_rate":  [ 10.0 ],
            "target_aws_balance":       [ 1000.0 ],
            "target_gce_vm_burn_rate":   [   9.0 ],
            "target_gce_balance":       [ 1000.0 ],
        }
        MyFP=FinancialParameters(myparams)
        mydf=MyFP.acquire(myparams)
        print mydf     

if __name__ == "__main__":
    main()
