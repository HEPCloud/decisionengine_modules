# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

""" Get job info from Nersc
"""
import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.NERSC.util import newt

_MAX_RETRIES = 10
_RETRY_BACKOFF_FACTOR = 1
# TODO this is a default column list and needs to be overriden from configuration


@Source.supports_config(
    Parameter(
        "constraints",
        type=dict,
        comment="""Supported dictionary structure:
  {
     machines: ["edison", "cori"],
     newt_keys: {
       user: ["user1", "user2"],
       repo: ['m2612', 'm2696'],
       features: ["knl&quad&cache"]
     }
  }""",
    ),
    Parameter("max_retries", default=_MAX_RETRIES),
    Parameter("retry_backoff_factor", default=_RETRY_BACKOFF_FACTOR),
    Parameter("passwd_file", type=str),
)
@Source.produces(Nersc_Job_Info=pd.DataFrame)
class NerscJobInfo(Source.Source):
    """
    Information of jobs on NERSC machines
    """

    def __init__(self, config):
        super().__init__(config)
        self.constraints = config.get("constraints")
        self.max_retries = config.get("max_retries", _MAX_RETRIES)
        self.retry_backoff_factor = config.get("retry_backoff_factor", _RETRY_BACKOFF_FACTOR)
        self.newt = newt.Newt(
            config.get("passwd_file"), max_retries=self.max_retries, retry_backoff_factor=self.retry_backoff_factor
        )

    def acquire(self):
        """
        Method to be called from Task Manager.
        redefines acquire from Source.py.
        Acquire NERSC job info and return as pandas frame
        :return: `dict`
        """
        self.logger.debug("in NerscJobInfo acquire")
        raw_results = []
        # By default, query edison and cori
        self.constraints["machines"] = self.constraints.get("machines", ["edison", "cori"])
        # get all systems that are up
        up_machines = [x for x in self.newt.get_status() if x["status"] == "up"]
        if not up_machines:
            self.logger.info("All machines at NERSC are down")
        # filter machines that are up
        machines = [x for x in self.constraints.get("machines") if x in [y["system"] for y in up_machines]]
        if not machines:
            self.logger.info("All requested machines at NERSC are down")
        # filter results based on constraints specified in newt_keys dictionary
        newt_keys = self.constraints.get("newt_keys", {})
        for m in machines:
            values = self.newt.get_queue(m)
            for k, v in newt_keys.items():
                if v:
                    values = [x for x in values if x[k] in v]
            if values:
                raw_results.extend(values)

        pandas_frame = pd.DataFrame(raw_results)
        return {"Nersc_Job_Info": pandas_frame}


Source.describe(NerscJobInfo)
