import os
import pytest
import mock
import pprint
import utils
from decisionengine.modules.glideinwms.sources import factory_global
from decisionengine.modules.htcondor import htcondor_query


config = {
    'condor_config': 'condor_config',
    'collector_host': 'fermicloud122.fnal.gov:8618',
    #'classad_attrs': ['Name', 'EntryName', 'GLIDEIN_Gatekeeper', 'GLIDEIN_GridType'],
}


class TestFactoryGlobalManifests:

    def test_produces(self):
        factory_global = factory_global.FactoryGlobalManifests(config)
        produces = ['factoryglobal_manifests']
        assert(factory_global.produces() == produces)


    def test_acquire(self):
        factory_global = factory_global.FactoryGlobalManifests(config)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file('factory_global.cs.fixture')
            pprint.pprint(factory_global.acquire())


    def test_acquire_live(self):
        factory_global = factory_global.FactoryGlobalManifests(config)
        pprint.pprint(factory_global.acquire())
