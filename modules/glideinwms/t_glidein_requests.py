#!/usr/bin/python

import argparse
import pprint
import pandas

from decisionengine.framework.modules import de_logger
from decisionengine.framework.modules import Transform
from decisionengine.framework.dataspace.datablock import DataBlock
from decisionengine.modules.glideinwms.glide_frontend_element import GlideFrontendElement

PRODUCES = ['glideclientglobal_manifests', 'glideclient_manifests']

CONSUMES = [
    'gwms_fe_config', 'factoryglobal_manifests', 'job_manifests',
    'Factory_Entries_LCF', 'startd_manifests', 'Factory_Entries_AWS'
]

SUPPORTED_ENTRY_TYPES = [
    'Factory_Entries_LCF', 'Factory_Entries_AWS', 'Factory_Entries_Grid'
]

# TODO: Extend to use following in future
# 'Nersc_Job_Info', 'Nersc_Allocation_Info'

class GlideinRequestManifests(Transform.Transform):

    def __init__(self, *args, **kwargs):
        super(GlideinRequestManifests, self).__init__(*args, **kwargs)
        if args:
            config = args[0]
        else:
            config = {}

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        # VO to which this transform should be applied
        self.acct_group = config.get('accounting_group', 'CMS')
        # Filter to further select jobs matching the criteria
        self.job_filter = config.get('job_filter', 'ClusterId > 0')
        # FE config group to get settings from
        self.fe_group = config.get('fe_config_group', 'CMS')

        self.logger = de_logger.get_logger()


    def consumes(self):
        """
        Return list of items consumed
        """
        return CONSUMES


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def transform(self, datablock):
        """
        Make all necessary calculations

        :type datablock: :obj:`~datablock.DataBlock`
        :arg datablock: data block

        :rtype: pandas frame (:class:`pd.DataFramelist`)
        """

        # Get the frontend config dict
        fe_cfg = datablock.get('gwms_fe_config')
        # Get factory global classad dataframe
        factory_globals = datablock.get('factoryglobal_manifests')
        # Initialize an empty DataFrame so we can copy factory entries
        entries = pandas.DataFrame()
        # Get factory entries dataframe for different type of entries
        for et in SUPPORTED_ENTRY_TYPES:
            entries = entries.append(datablock.get(et), ignore_index=True)

        # Get the jobs dataframe
        jobs_df = datablock.get('job_manifests')
        # Get HTCondor slots dataframe
        slots_df = datablock.get('startd_manifests')

        glide_frontend_element = GlideFrontendElement(self.fe_group,
                                                      self.acct_group, fe_cfg)
        manifests = glide_frontend_element.generate_glidein_requests(
            jobs_df, slots_df, entries, factory_globals,
            job_filter=self.job_filter)

        return manifests


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        't_clientglobal_manifests': {
            'module': 'modules.glideinwms.t_client_global',
            'name': 'GlideinRequestManifests',
            'parameters': {
            }
        }
    }
    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print('produces %s' % PRODUCES)
    module_config_template()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configtemplate',
        action='store_true',
        help='prints the expected module configuration')

    parser.add_argument(
        '--configinfo',
        action='store_true',
        help='prints config template along with produces and consumes info')
    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == '__main__':
    main()
