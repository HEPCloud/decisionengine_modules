import os
import pprint
import time

import mock

from decisionengine_modules.util import testutils as utils
from decisionengine_modules.glideinwms.sources import factory_entries
from decisionengine_modules.htcondor import htcondor_query

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "factory_entries.cs.fixture")

CONFIG_FACTORY_ENTRIES = {
    'condor_config': 'condor_config',
    'factories': [
        {
            'collector_host': 'cmssrv280.fnal.gov',
        },
    ]
}

CONFIG_FACTORY_ENTRIES_BAD = {
    'condor_config': 'condor_config',
    'factories': [
        {
            'collector_host': 'dummy_collector.fnal.gov',
        },
    ]
}

CONFIG_FACTORY_ENTRIES_BAD_WITH_TIMEOUT = {
    'condor_config': 'condor_config',
    'nretries': 2,
    'retry_interval': 2,
    'factories': [
        {
            'collector_host': 'dummy_collector.fnal.gov',
        },
    ]
}


class TestFactoryEntries:

    def test_produces(self):
        entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES)
        produces = [
            'Factory_Entries_Grid', 'Factory_Entries_AWS',
            'Factory_Entries_GCE', 'Factory_Entries_LCF'
        ]
        assert(entries.produces() == produces)

    def test_acquire(self):
        entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            pprint.pprint(entries.acquire())

    def test_acquire_live(self):
        entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES)
        pprint.pprint(entries.acquire())

    def test_acquire_bad(self):
        entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES_BAD)
        result = entries.acquire()
        for df in result.values():
            assert(df.dropna().empty is True)

    def test_acquire_bad_with_timeout(self):
        entries = factory_entries.FactoryEntries(
            CONFIG_FACTORY_ENTRIES_BAD_WITH_TIMEOUT)
        start = time.time()
        result = entries.acquire()
        end = time.time()
        # Set by tuning nretries and the retry_interval
        assert(end - start > 5)
        for df in result.values():
            assert(df.dropna().empty is True)
