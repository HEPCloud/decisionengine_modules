# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os
import pprint

from unittest import mock

import pandas

from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.htcondor.sources import job_q
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "cq.fixture")

CONFIG_CQ = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "collector_host": "fermicloud122.fnal.gov",
    "schedds": ["fermicloud122.fnal.gov"],
    "classad_attrs": ["ClusterId", "ProcId", "JobStatus"],
}


def test_produces():
    jq = job_q.JobQ(CONFIG_CQ)
    assert jq._produces == {"job_manifests": pandas.DataFrame}


def test_condorq():
    jq = job_q.JobQ(CONFIG_CQ)
    with mock.patch.object(htcondor_query.CondorQ, "fetch") as f:
        f.return_value = utils.input_from_file(FIXTURE_FILE)
        pprint.pprint(jq.acquire())


def test_condorq_live():
    jq = job_q.JobQ(CONFIG_CQ)
    pprint.pprint(jq.acquire())
