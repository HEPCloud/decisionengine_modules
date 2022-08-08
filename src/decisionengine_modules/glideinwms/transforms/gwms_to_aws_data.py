# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas as pd

from decisionengine.framework.modules import Transform

_ATTR_TRANSLATION_MAP = {
    "GLIDEIN_Supported_VOs": "AWSProfile",
    "INSTANCE_TYPE": "InstanceType",
    "AVAILABILITY_ZONE": "AvailabilityZone",
    "GlideinConfigPerEntryMaxGlideins": "MaxLimit",
}


@Transform.consumes(Factory_Entries=pd.DataFrame)
@Transform.produces(aws_instance_limits=pd.DataFrame, spot_occupancy_config=pd.DataFrame)
class AWSFactoryEntryData(Transform.Transform):
    def __init__(self, config):
        super().__init__(config)

    def transform(self, datablock):

        # Get the dataframe containing AWS entries
        self.logger.debug("in AWSFactoryEntryData transform")
        aws_entries = self.Factory_Entries(datablock).xs("AWS")

        limits_df = pd.DataFrame()
        so_config_dict = {}

        if not aws_entries.empty:
            # Get relevant columns from the dataframe
            sub_df = aws_entries[_ATTR_TRANSLATION_MAP.keys()]

            """
            GLIDEIN_Supported_VOs can be list of comma separated strings.
            Convert it into flat list of string
            """
            vos = [i for sublist in [x.split(",") for x in list(sub_df.GLIDEIN_Supported_VOs)] for i in sublist]
            # unique VOs
            vo_set = set(vos)

            # Convert to relevant aws data and config
            for vo in vo_set:
                if vo:
                    df = sub_df.loc[
                        sub_df["GLIDEIN_Supported_VOs"].str.contains(vo),
                        ["INSTANCE_TYPE", "AVAILABILITY_ZONE", "GlideinConfigPerEntryMaxGlideins"],
                    ]
                    df["GLIDEIN_Supported_VOs"] = vo
                    if limits_df is None:
                        limits_df = df
                    else:
                        limits_df = limits_df.append(df, ignore_index=True)

                    az_it = sub_df.loc[
                        sub_df["GLIDEIN_Supported_VOs"].str.contains(vo), ["INSTANCE_TYPE", "AVAILABILITY_ZONE"]
                    ]
                    regions = {az[:-1] for az in az_it.AVAILABILITY_ZONE.unique()}
                    so_config_dict[vo] = {}
                    for region in regions:
                        it = az_it.loc[az_it["AVAILABILITY_ZONE"].str.contains(region)].INSTANCE_TYPE.unique().tolist()
                        so_config_dict[vo][region] = it

            limits_df = limits_df.rename(columns=_ATTR_TRANSLATION_MAP)

        return {"aws_instance_limits": limits_df, "spot_occupancy_config": pd.DataFrame.from_dict(so_config_dict)}


Transform.describe(AWSFactoryEntryData)
