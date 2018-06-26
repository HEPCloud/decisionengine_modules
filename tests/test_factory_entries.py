import os
import pytest
import mock
import pprint
import utils
from decisionengine_modules.glideinwms.sources import factory_entries
from decisionengine_modules.htcondor import htcondor_query


config_factory_entries = {
    'condor_config': 'condor_config',
    'collector_host': 'fermicloud122.fnal.gov:8618',
    #'classad_attrs': ['Name', 'EntryName', 'GLIDEIN_Gatekeeper', 'GLIDEIN_GridType'],
}


class TestFactoryEntries:

    def test_produces(self):
        entries = factory_entries.FactoryEntries(config_factory_entries)
        produces = [
            'Factory_Entries_Grid', 'Factory_Entries_AWS',
            'Factory_Entries_GCE', 'Factory_Entries_LCF'
        ]
        assert(entries.produces() == produces)


    def test_acquire(self):
        entries = factory_entries.FactoryEntries(config_factory_entries)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file('factory_entries.cs.fixture')
            pprint.pprint(entries.acquire())


    def test_acquire_live(self):
        entries = factory_entries.FactoryEntries(config_factory_entries)
        pprint.pprint(entries.acquire())
