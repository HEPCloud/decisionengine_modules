#!/usr/bin/python

import argparse
import pprint
import pandas as pd

from decisionengine.framework.modules import Transform

PRODUCES = ['aws_instance_limits', 'spot_occupancy_config']

CONSUMES = ['Factory_Entries_AWS']

_ATTR_TRANSLATION_MAP = {
    'GLIDEIN_Supported_VOs': 'AWSProfile',
    'INSTANCE_TYPE': 'InstanceType',
    'AVAILABILITY_ZONE': 'AvailabilityZone',
    'GlideinConfigPerEntryMaxGlideins': 'MaxLimit',
}


class AWSFactoryEntryData(Transform.Transform):

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

        # Get the dataframe containing AWS entries
        aws_entries = datablock.get(CONSUMES[0])

        limits_df = pd.DataFrame()
        so_config_dict = {}

        if not aws_entries.empty:
            # Get relevant columns from the dataframe
            sub_df = aws_entries[_ATTR_TRANSLATION_MAP.keys()]

            """
            GLIDEIN_Supported_VOs can be list of comma separated strings.
            Convert it into flat list of string
            """
            vos = [i for sublist in
                   [x.split(",") for x in list(sub_df.GLIDEIN_Supported_VOs)]
                   for i in sublist]
            # unique VOs
            vo_set = set(vos)

            # Convert to relevant aws data and config
            for vo in vo_set:
                if vo:
                    df = sub_df.loc[sub_df['GLIDEIN_Supported_VOs'].str.contains(vo), ['INSTANCE_TYPE', 'AVAILABILITY_ZONE', 'GlideinConfigPerEntryMaxGlideins']]
                    df['GLIDEIN_Supported_VOs'] = vo
                    if limits_df is None:
                        limits_df = df
                    else:
                        limits_df = limits_df.append(df, ignore_index=True)

                    az_it = sub_df.loc[sub_df['GLIDEIN_Supported_VOs'].str.contains(vo), ['INSTANCE_TYPE', 'AVAILABILITY_ZONE']]
                    regions = set([az[:-1] for az in az_it.AVAILABILITY_ZONE.unique()])
                    so_config_dict[vo] = {}
                    for region in regions:
                        it = az_it.loc[az_it['AVAILABILITY_ZONE'].str.contains(region)].INSTANCE_TYPE.unique().tolist()
                        so_config_dict[vo][region] = it

            limits_df = limits_df.rename(columns=_ATTR_TRANSLATION_MAP)

        return {'aws_instance_limits': limits_df,
                'spot_occupancy_config': pd.DataFrame.from_dict(so_config_dict)}


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'gwms_to_aws_data': {
            'module': 'modules.glideinwms.t_gwms_to_aws_config',
            'name': 'AWSFactoryEntryData',
            'parameters': '{}',
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
