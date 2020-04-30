"""
Calculates real time burn rate for AWS

"""
import pandas as pd
import pprint

from decisionengine.framework.modules import Transform
import logging

"""
IMPORTANT: Please do not change order of these keys and always
           append new keys rather than pre-pend or insert.
"""

CONSUMES = ["provisioner_resource_spot_prices",
            "AWS_Occupancy"]

PRODUCES = ["AWS_Burn_Rate"]


class AwsBurnRate(Transform.Transform):
    def __init__(self, config):
        super(AwsBurnRate, self).__init__(config)
        self.logger = logging.getLogger()

    def transform(self, data_block):

        spot_prices = data_block[CONSUMES[0]].fillna(0)
        occupancy = data_block[CONSUMES[1]].fillna(0)

        burn_df = pd.DataFrame([{"BurnRate": 0.}])
        if not occupancy.empty:
            df = pd.merge(occupancy,
                          spot_prices,
                          how="inner",
                          on=["AccountName", "AvailabilityZone", "InstanceType"])
            if not df.empty:
                df["BurnRate"] = pd.to_numeric(
                    df["RunningVms"]) * pd.to_numeric(df["SpotPrice"])
                burn_df = pd.DataFrame([{"BurnRate": df["BurnRate"].sum()}])

        return {PRODUCES[0]: burn_df}

    def consumes(self, name_list=None):
        return CONSUMES

    def produces(self, name_schema_id_list=None):
        return PRODUCES


def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {
        "AwsBurnRate": {
            "module": "modules.AWS.transforms.AwsBurnRate",
            "name": "AwsBurnRate",
            "parameters": {
            }
        }
    }

    print("Entry in channel cofiguration")
    pprint.pprint(d)
    print("where")
    print("\t name - name of the class to be instantiated by task manager")


def module_config_info():
    """
    print this module configuration information
    """

    print("consumes", CONSUMES)
    print("produces", PRODUCES)
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
