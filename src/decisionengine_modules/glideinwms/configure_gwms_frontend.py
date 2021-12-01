# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import os.path
import sys

import glideinwms.creation.lib.cvWConsts
import glideinwms.creation.lib.cvWDictFile
import glideinwms.creation.lib.cvWParamDict
import glideinwms.creation.lib.cvWParams
import glideinwms.creation.lib.cWConsts
import glideinwms.creation.lib.xslt

from decisionengine_modules.glideinwms import glideinwms_config_lib
from decisionengine_modules.glideinwms.DEConfigSource import DEConfigSource
from decisionengine_modules.glideinwms.UniversalFrontendParams import UniversalFrontendParams


def main(args):
    # Load params from the decision engine configuration
    print("...Loading GlideinWMS module configuration from the decision engine ...")
    params = UniversalFrontendParams(args.web_base_dir, DEConfigSource())

    # Create dictionaries for new params
    frontend_dicts_obj = glideinwms.creation.lib.cvWParamDict.frontendDicts(params)
    frontend_dicts_obj.populate()

    if args.update_scripts == "yes":
        # Update scripts will always be true.
        frontend_dicts_obj.create_dirs(fail_if_exists=False)

    # Write contents to disk
    frontend_dicts_obj.save()
    frontend_dicts_obj.set_readonly(True)

    fe_configuration = glideinwms_config_lib.FrontendConfiguration()
    fe_configuration.save(args.de_frontend_config, set_ro=True)

    print("...Saved frontend config for decision engine into the working dir")

    print(f"...Reconfigured frontend '{params.frontend_name}'")
    print("...Active groups are:")
    for entry in frontend_dicts_obj.active_sub_list:
        print(f"     {entry}")

    print(f"...Work files are in {frontend_dicts_obj.main_dicts.work_dir}")


def get_arg_parser():
    """
    Parse command line options
    """

    description = "Read the frontend configuration, update the web staging area and generate intermediate configuration that can be consumed by the decision engine"

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--de-frontend-config",
        action="store",
        dest="de_frontend_config",
        default="/var/lib/gwms-frontend/vofrontend/de_frontend_config",
        help="Full path to output configuration file for the DE module",
    )
    parser.add_argument(
        "--update-scripts", action="store_true", dest="update_scripts", help="Update the scripts in the working area"
    )
    parser.add_argument(
        "--web-base-dir",
        action="store",
        dest="web_base_dir",
        default="/var/lib/gwms-frontend/web-base",
        help="Location of the web base directory",
    )

    return parser


############################################################
#
# S T A R T U P
#
############################################################

if __name__ == "__main__":

    noroot_msg = "NOTE: Executing this command as user root is not allowed. Use the decisionengine user instead."

    if os.geteuid() == 0:
        print(noroot_msg)

    parser = get_arg_parser()
    args = parser.parse_args()

    try:
        main(args)
    except RuntimeError as e:
        print("\nError processing the configuration")
        print(e)
        sys.exit(1)
