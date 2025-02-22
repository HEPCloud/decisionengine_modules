# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Calculates price / performance and figure of merit and
saves it into the output file according to design document.

"""
import copy
import sys

import pandas as pd

from decisionengine.framework.modules import Transform

DEFAULT_MAX_LIMIT = 20
BIG_NUMBER = sys.float_info.max
LARGE_NUMBER = sys.float_info.max


def price_performance(SpotPrice, PerfTtbarTotal):
    pp = 0.0
    if float(PerfTtbarTotal) > 0.0:
        pp = float(SpotPrice) / float(PerfTtbarTotal)
    return pp


def figure_of_merit(RunningVms, MaxLimit, PricePerf):
    fm = LARGE_NUMBER
    if int(MaxLimit) > 0:
        if RunningVms < MaxLimit:
            fm = ((float(RunningVms) + 1) / int(MaxLimit)) * PricePerf
        else:
            fm = BIG_NUMBER
    return fm


@Transform.consumes(
    provisioner_resource_spot_prices=pd.DataFrame,
    Performance_Data=pd.DataFrame,
    aws_instance_limits=pd.DataFrame,
    AWS_Occupancy=pd.DataFrame,
)
@Transform.produces(AWS_Price_Performance=pd.DataFrame, AWS_Figure_Of_Merit=pd.DataFrame)
class FigureOfMerit(Transform.Transform):
    def __init__(self, config):
        super().__init__(config)

    def transform(self, data_block):
        """
        Make all necessary calculations

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block

        :rtype: pandas frame (:class:`pd.DataFramelist`)
        """
        self.logger.debug("in FigureOfMerit transform")
        spot_price_data = self.provisioner_resource_spot_prices(data_block)
        perf_data = self.Performance_Data(data_block)
        occup_data = self.AWS_Occupancy(data_block)
        job_limits_data = self.aws_instance_limits(data_block)

        price_perf_rows = []
        fom_rows = []
        for _i, row in spot_price_data.iterrows():
            if perf_data.empty:
                r1 = perf_data
            else:
                r1 = perf_data.loc[
                    (perf_data["AvailabilityZone"] == row["AvailabilityZone"])
                    & (perf_data["InstanceType"] == row["InstanceType"])
                ]

            if occup_data.empty:
                r2 = occup_data
            else:
                r2 = occup_data[
                    (occup_data["AvailabilityZone"] == row["AvailabilityZone"])
                    & (occup_data["InstanceType"] == row["InstanceType"])
                ]

            if job_limits_data.empty:
                r3 = job_limits_data
            else:
                r3 = job_limits_data[
                    (job_limits_data.AWSProfile == row["AccountName"])
                    & (job_limits_data["AvailabilityZone"] == row["AvailabilityZone"])
                    & (job_limits_data["InstanceType"] == row["InstanceType"])
                ]
            price_perf_row = copy.copy(row)
            fom_row = copy.copy(row)

            if r1.empty:
                price_perf_row["PerfTtbarTotal"] = 0.0
                fom_row["PerfTtbarTotal"] = 0.0
            else:
                price_perf_row["PerfTtbarTotal"] = r1["PerfTtbarTotal"].values[0]
                price_perf_row["EntryName"] = r1["EntryName"].values[0]
                fom_row["PerfTtbarTotal"] = r1["PerfTtbarTotal"].values[0]
                fom_row["EntryName"] = r1["EntryName"].values[0]

            if r2.empty:
                running_vms = 0
            else:
                running_vms = r2["RunningVms"].values[0]

            if r3.empty:
                price_perf_row["MaxLimit"] = DEFAULT_MAX_LIMIT
                fom_row["MaxLimit"] = DEFAULT_MAX_LIMIT
            else:
                price_perf_row["MaxLimit"] = r3["MaxLimit"].values[0]
                fom_row["MaxLimit"] = r3["MaxLimit"].values[0]

            price_perf = price_performance(row["SpotPrice"], price_perf_row["PerfTtbarTotal"])
            price_perf_row["AWS_Price_Performance"] = price_perf
            fom_row["AWS_Figure_Of_Merit"] = figure_of_merit(running_vms, price_perf_row["MaxLimit"], price_perf)
            price_perf_rows.append(price_perf_row)
            fom_rows.append(fom_row)

        price_perf_df = pd.DataFrame(price_perf_rows)
        price_perf_df.reindex(sorted(price_perf_df.columns), axis=1)
        fom_df = pd.DataFrame(fom_rows)
        fom_df.reindex(sorted(fom_df.columns), axis=1)
        return {"AWS_Price_Performance": price_perf_df, "AWS_Figure_Of_Merit": fom_df}


Transform.describe(FigureOfMerit)
