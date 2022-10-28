# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Fill in data from Job Limits CSV file
"""
import os
import time

import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter

_RETRIES = 5
_TO = 20


@Source.supports_config(Parameter("data_file", type=str, comment="CSV job limits data file"))
@Source.produces(Job_Limits=pd.DataFrame)
class AWSJobLimits(Source.Source):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.data_file = config["data_file"]

    def acquire(self):
        self.logger.debug("in AWSJobLimits acquire")
        rc = None
        for _ in range(_RETRIES):
            if os.path.exists(self.data_file):
                rc = {
                    "Job_Limits": pd.read_csv(self.data_file)
                    .drop_duplicates(subset=["AvailabilityZone", "InstanceType"], keep="last")
                    .reset_index(drop=True)
                }
                break
            else:
                time.sleep(_TO)
        return rc


Source.describe(AWSJobLimits)
