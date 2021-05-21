import os
import pandas
import pprint
import time

import mock

from decisionengine_modules.util import testutils as utils
from decisionengine_modules.glideinwms.sources import factory_global
from decisionengine_modules.htcondor import htcondor_query

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "factory_global.cs.fixture")

CONFIG = {
    'condor_config': 'condor_config',
    'factories': [
        {
            'collector_host': 'cmssrv280.fnal.gov',
        },
    ]
}

CONFIG_BAD = {
    'condor_config': 'condor_config',
    'factories': [
        {
            'collector_host': 'dummy_collector.fnal.gov',
        },
    ]
}

CONFIG_BAD_WITH_TIMEOUT = {
    'condor_config': 'condor_config',
    'nretries': 2,
    'retry_interval': 2,
    'factories': [
        {
            'collector_host': 'dummy_collector.fnal.gov',
        },
    ]
}


class TestFactoryGlobalManifests:

    def test_produces(self):
        fg = factory_global.FactoryGlobalManifests(CONFIG)
        assert fg._produces == {'factoryglobal_manifests': pandas.DataFrame}

    def test_acquire(self):
        fg = factory_global.FactoryGlobalManifests(CONFIG)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            pprint.pprint(fg.acquire())

    def test_acquire_live(self):
        fg = factory_global.FactoryGlobalManifests(CONFIG)
        pprint.pprint(fg.acquire())

    def test_acquire_bad(self):
        fg = factory_global.FactoryGlobalManifests(CONFIG_BAD)
        fg_df = fg.acquire()
        assert((fg_df['factoryglobal_manifests'] is None) or
               (len(fg_df['factoryglobal_manifests']) == 0))

    def test_acquire_bad_with_timeout(self):
        fg = factory_global.FactoryGlobalManifests(CONFIG_BAD_WITH_TIMEOUT)
        start = time.time()
        fg_df = fg.acquire()
        end = time.time()
        # Set by tuning nretries and the retry_interval
        assert(end - start > 5)
        assert((fg_df['factoryglobal_manifests'] is None) or
               (len(fg_df['factoryglobal_manifests']) == 0))
