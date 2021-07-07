import os
import pandas
import pprint
import time

from unittest import mock

from decisionengine_modules.util import testutils as utils
from decisionengine_modules.glideinwms.sources import factory_entries
from decisionengine_modules.htcondor import htcondor_query

import pandas as pd

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

CONFIG_FACTORY_ENTRIES_CORMAP = {
    "condor_config": "/etc/condor/condor_config",
    "factories": [
        {
            "collector_host": "dummy_collector.fnal.gov",
            "classad_attrs": ['GLIDEIN_GridType', "GLIDEIN_CMSSite", 'GLIDEIN_Resource_Slots'],
            "correction_map": {
                "GLIDEIN_Resource_Slots":'DummySlots',
                "GLIDEIN_CMSSite":'DummySite'
            }
            },
    ]
}

class TestFactoryEntries:

    def test_produces(self):
        entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES)
        produces = dict.fromkeys(['Factory_Entries_Grid', 'Factory_Entries_AWS',
                                  'Factory_Entries_GCE', 'Factory_Entries_LCF'],
                                 pandas.DataFrame)
        assert(entries._produces == produces)

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

    def test_acquire_correctionmap(self):
        d1 = {'GLIDEIN_Resource_Slots': ['DummySlots', 'DummySlots'] }
        d2 = {'GLIDEIN_CMSSite': ['DummySite', 'DummySite'] }
        df1 = pd.DataFrame(data=d1)
        df2 = pd.DataFrame(data=d2)

        entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES_CORMAP)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            dummypd = entries.acquire()
            dummypd2 = dummypd['Factory_Entries_Grid']
            assert( df1.equals( dummypd2[['GLIDEIN_Resource_Slots']]) )
            assert( df2.equals( dummypd2[['GLIDEIN_CMSSite']]) )
