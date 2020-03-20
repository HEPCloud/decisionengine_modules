#!/usr/bin/env python

#from __future__ import print_function
import os
import sys
import tempfile
import os.path
import argparse

import glideinwms.creation.lib.cvWParams
import glideinwms.creation.lib.cvWDictFile
import glideinwms.creation.lib.cWConsts
import glideinwms.creation.lib.cvWConsts
import glideinwms.creation.lib.cvWParamDict
import glideinwms.creation.lib.xslt

from . import glideinwms_config_lib


def frontend_to_de_config(frontend_workdir='/var/lib/gwms-frontend/vofrontend'):
    fe_configuration = glideinwms_config_lib.FrontendConfiguration(
        frontend_workdir=frontend_workdir)
    return fe_configuration.frontend_config


def main(args):

    # Load params from frontend configuration file
    print('...Loading frontend configuration from %s ...' %
          args.frontend_config)
    params = load_params_from_config(args, usage=usage)

    # Create dictionaries for new params
    frontend_dicts_obj = glideinwms.creation.lib.cvWParamDict.frontendDicts(
        params)
    frontend_dicts_obj.populate()

    if args.update_scripts == 'yes':
        # Update scripts will always be true.
        frontend_dicts_obj.create_dirs(fail_if_exists=False)

    # load old files and merge them together
    # if old_params is not None:
    #    old_frontend_dicts_obj = cvWParamDict.frontendDicts(old_params)
    #    old_frontend_dicts_obj.load()
    #    frontend_dicts_obj.reuse(old_frontend_dicts_obj)

    # Write contents to disk
    frontend_dicts_obj.save()
    frontend_dicts_obj.set_readonly(True)
    cfgfile = os.path.join(frontend_dicts_obj.main_dicts.work_dir,
                           glideinwms.creation.lib.cvWConsts.XML_CONFIG_FILE)

    # save config into file (with backup, since the old one already exists)
    # This is the current working version of the frontend in the
    # frontend instance dir
    params.save_into_file_wbackup(cfgfile, set_ro=True)
    print("...Saved the current config file into the working dir")

    # make backup copy that does not get overwritten on further reconfig
    # This file is has a hash on the extension and is located in the
    # frontend instance dir
    cfgfile = glideinwms.creation.lib.cWConsts.insert_timestr(cfgfile)
    params.save_into_file(cfgfile, set_ro=True)
    print("...Saved the backup config file into the working dir")

    fe_configuration = glideinwms_config_lib.FrontendConfiguration()
    fe_configuration.save(args.de_frontend_config, set_ro=True)

    print("...Saved frontend config for decision engine into the working dir")

    print("...Reconfigured frontend '%s'" % params.frontend_name)
    print("...Active groups are:")
    for entry in frontend_dicts_obj.active_sub_list:
        print("     %s" % entry)

    print("...Work files are in %s" % frontend_dicts_obj.main_dicts.work_dir)


def get_arg_parser():
    """
    Parse command line options
    """

    description = 'Read the frontend configuration, update the web staging area and generate intermediate configuration that can be consumed by the decision engine'

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--frontend-config', action='store', dest='frontend_config',
        default='/etc/gwms-frontend/frontend.xml',
        help='Full path to the GlideinWMS frontend configuration file')
    parser.add_argument(
        '--de-frontend-config', action='store', dest='de_frontend_config',
        default='/var/lib/gwms-frontend/vofrontend/de_frontend_config',
        help='Full path to output configuration file for the DE module')
    parser.add_argument(
        '--update-scripts', action='store_true', dest='update_scripts',
        help='Update the scripts in the working area')
    parser.add_argument(
        '--xslt-plugin-dir', action='store', dest='xslt_plugin_dir',
        default=None,
        help='Location of the xslt plugin directory. NOT SUPPORTED.')
    parser.add_argument(
        '--web-base-dir', action='store', dest='web_base_dir',
        default='/var/lib/gwms-frontend/web-base',
        help='Location of the web base directory')

    return parser


def load_params_from_config(args, usage=''):
    try:
        transformed_xmlfile = tempfile.NamedTemporaryFile()
        transformed_xmlfile.write(
            glideinwms.creation.lib.xslt.xslt_xml(
                old_xmlfile=args.frontend_config,
                xslt_plugin_dir=args.xslt_plugin_dir))
        transformed_xmlfile.flush()
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    params = glideinwms.creation.lib.cvWParams.VOFrontendParams(
        usage, args.web_base_dir,
        [sys.argv[0], transformed_xmlfile.name])
    params.cfg_name = args.frontend_config
    return params


def get_old_params(params, args):
    # This is the current running version, saved in the frontend work dir
    old_config_file = os.path.join(
        params.work_dir, glideinwms.creation.lib.cvWConsts.XML_CONFIG_FILE)
    # print old_config_file
    if os.path.exists(old_config_file):
        try:
            old_params = glideinwms.creation.lib.cvWParams.VOFrontendParams(
                args.usage, args.web_base_dir,
                [sys.argv[0], old_config_file])
        except RuntimeError as e:
            raise RuntimeError('Failed to load %s' % old_config_file)
    else:
        print('Warning: Cannot find %s' % old_config_file)
        print('Ignore above warning if this is the first reconfig')
        old_params = None

    return old_params

############################################################
#
# S T A R T U P
#
############################################################


if __name__ == '__main__':

    noroot_msg = 'NOTE: Executing this command as user root is not allowed. Use the decisionengine user instead.'

    if os.geteuid() == 0:
        print(noroot_msg)

    parser = get_arg_parser()
    args = parser.parse_args()
    usage = parser.format_usage()

    try:
        main(args)
    except RuntimeError as e:
        print('\nError processing the configuration %s:' %
              args.frontend_config)
        print(e)
        sys.exit(1)
