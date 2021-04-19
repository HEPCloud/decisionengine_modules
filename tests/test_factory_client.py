import os
import pandas
import pprint

import mock

from decisionengine_modules.glideinwms.sources import factory_client
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "factory_client.cs.fixture")

CONFIG = {
    'condor_config': 'condor_config',
    'collector_host': 'cmssrv280.fnal.gov',
}

CONFIG_BAD = {
    'condor_config': 'condor_config',
    'collector_host': 'dummy_collector.fnal.gov',
}


class TestFactoryClientManifests:

    def test_produces(self):
        fc = factory_client.FactoryClientManifests(CONFIG)
        assert fc._produces == {'factoryclient_manifests': pandas.DataFrame}

    def test_acquire(self):
        fc = factory_client.FactoryClientManifests(CONFIG)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            pprint.pprint(fc.acquire())

    def test_acquire_live(self):
        fc = factory_client.FactoryClientManifests(CONFIG)
        pprint.pprint(fc.acquire())

    def test_acquire_bad(self):
        fc = factory_client.FactoryClientManifests(CONFIG_BAD)
        fc_df = fc.acquire()
        assert(len(fc_df['factoryclient_manifests']) == 0)
