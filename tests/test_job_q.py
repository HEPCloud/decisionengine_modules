import os
import pprint

import mock

import utils
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.htcondor.sources import job_q

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "cq.fixture")

CONFIG_CQ = {
    "condor_config": "condor_config",
    "collector_host": "fermicloud122.fnal.gov",
    "schedds": ["fermicloud122.fnal.gov"],
    "classad_attrs": ["ClusterId", "ProcId", "JobStatus"]
}


class TestJobQ:

    def test_produces(self):
        produces = ["job_manifests"]
        jq = job_q.JobQ(CONFIG_CQ)
        assert(jq.produces() == produces)

    def test_condorq(self):
        jq = job_q.JobQ(CONFIG_CQ)
        with mock.patch.object(htcondor_query.CondorQ, "fetch") as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            pprint.pprint(jq.acquire())

    def test_condorq_live(self):
        jq = job_q.JobQ(CONFIG_CQ)
        pprint.pprint(jq.acquire())
