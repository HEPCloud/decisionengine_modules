import os
import pprint

import mock

from decisionengine_modules.util import testutils as utils
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.htcondor.sources import slots

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "cs.fixture")

CONFIG = {
    'condor_config': 'condor_config',
    'collector_host': 'fermicloud122.fnal.gov',
}


class TestStartdManifests:

    def test_produces(self):
        produces = ['startd_manifests']
        s = slots.StartdManifests(CONFIG)
        assert(s.produces() == produces)

    def test_acquire(self):
        s = slots.StartdManifests(CONFIG)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            pprint.pprint(s.acquire())
