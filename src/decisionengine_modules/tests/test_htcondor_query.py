# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

from unittest import mock

from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "cs.fixture")

config_cq = {
    "condor_config": "condor_config",
    "pool_name": "dummy_collector.fnal.gov, cmssrv274.fnal.gov",
    "schedd_name": "hepcjobsub01.fnal.gov",
}

config_cs = {
    "condor_config": "condor_config",
    "pool_name": "dummy_collector.fnal.gov, cmssrv274.fnal.gov",
}

config_cq_bad = {
    "condor_config": "condor_config",
    "pool_name": "dummy_collector.fnal.gov, bad_collector.fnal.gov",
    "schedd_name": "hepcjobsub01.fnal.gov",
}

config_cs_bad = {
    "condor_config": "condor_config",
    "pool_name": "dummy_collector.fnal.gov, bad_collector.fnal.gov",
}


class TestCondorQ:
    def test_condorq_queryerror(self):
        condor_q = htcondor_query.CondorQ(
            schedd_name=config_cq_bad.get("schedd_name"), pool_name=config_cq_bad.get("pool_name")
        )
        try:
            condor_q.load(constraint="procid < 2")
            assert False
        except htcondor_query.QueryError:
            assert True

    def test_condorq(self):
        condor_q = htcondor_query.CondorQ(
            schedd_name=config_cq.get("schedd_name"), pool_name=config_cq.get("pool_name")
        )

        with mock.patch.object(htcondor_query.CondorQ, "fetch") as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            condor_q.load()
            assert f.return_value == condor_q.stored_data


class TestCondorStatus:
    def test_condorstatus_queryerror(self):
        condor_status = htcondor_query.CondorStatus(pool_name=config_cs_bad.get("pool_name"))

        try:
            condor_status.load()
            assert False
        except htcondor_query.QueryError:
            assert True

    def test_condorstatus(self):
        condor_status = htcondor_query.CondorStatus(subsystem_name="any", pool_name=config_cs.get("pool_name"))

        with mock.patch.object(htcondor_query.CondorStatus, "fetch") as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            condor_status.load()
            assert f.return_value == condor_status.stored_data
