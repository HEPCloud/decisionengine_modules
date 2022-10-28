# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os
import pprint

from unittest import mock

import pandas
import pytest

from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.htcondor.sources import job_q
from decisionengine_modules.util import testutils as utils

FIXTURE_FILE = os.path.join(os.path.dirname(__file__), "data", "cq.fixture")


@pytest.fixture
def jobq_instance():
    config = {
        "channel_name": "test",
        "condor_config": "condor_config",
        "collector_host": "fermicloud122.fnal.gov",
        "schedds": ["fermicloud122.fnal.gov"],
        "classad_attrs": ["ClusterId", "ProcId", "JobStatus"],
    }
    return job_q.JobQ(config, logger=None)


def test_produces(jobq_instance):
    assert jobq_instance._produces == {"job_manifests": pandas.DataFrame}


def test_condorq(jobq_instance):
    with mock.patch.object(htcondor_query.CondorQ, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        pprint.pprint(jobq_instance.acquire())


def test_condorq_live(jobq_instance):
    pprint.pprint(jobq_instance.acquire())
