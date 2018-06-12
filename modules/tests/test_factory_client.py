import os
import pytest
import mock
import pprint
import utils
from decisionengine.modules.glideinwms.sources import factory_client
from decisionengine.modules.htcondor import htcondor_query


config = {
    'condor_config': 'condor_config',
    'collector_host': 'fermicloud122.fnal.gov:8618',
    #'classad_attrs': ['Name', 'EntryName', 'GLIDEIN_Gatekeeper', 'GLIDEIN_GridType'],
}


class TestFactoryClientManifests:

    def test_produces(self):
        factory_client = factory_client.FactoryClientManifests(config)
        produces = ['factoryclient_manifests']
        assert(factory_client.produces() == produces)


    def test_acquire(self):
        factory_client = factory_client.FactoryClientManifests(config)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file('factory_client.cs.fixture')
            pprint.pprint(factory_client.acquire())


    def test_acquire_live(self):
        factory_client = factory_client.FactoryClientManifests(config)
        pprint.pprint(factory_client.acquire())
