import os
import pytest
import mock
import pprint

import classad

from decisionengine.modules.glideinwms import factory_entries
from decisionengine.modules.htcondor import htcondor_query


config_factory_entries = {
    'condor_config': 'condor_config',
    'collector_host': 'fermicloud122.fnal.gov:8618',
    #'classad_attrs': ['Name', 'EntryName', 'GLIDEIN_Gatekeeper', 'GLIDEIN_GridType'],
}

def prepare_dict_from_file(fname):
    with open(fname) as fd:
        return eval(fd.read())
        #return (eval(fd.read())).values()

def prepare_condorstatus_dict():
    return prepare_dict_from_file('factory_entries.cs.fixture')


def prepare_condorq_dict():
    return prepare_dict_from_file('cq.fixture')


class TestFactoryEntries:

    def test_produces(self):
        entries = factory_entries.FactoryEntries(config_factory_entries)
        produces = [
            'Factory_Entries_Grid', 'Factory_Entries_AWS',
            'Factory_entries_GCE', 'Factory_Entries_LCF'
        ]
        assert(entries.produces() == produces)

    def test_acquire(self):
        entries = factory_entries.FactoryEntries(config_factory_entries)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = prepare_condorstatus_dict()
            pprint.pprint(entries.acquire())
