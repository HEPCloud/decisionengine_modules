import os
import pytest
import mock
import pprint
import utils
from decisionengine.modules.htcondor import htcondor_query
from decisionengine.modules.htcondor.sources import slots


config_cs = {
    'condor_config': 'condor_config',
    'collector_host': 'fermicloud122.fnal.gov',
}


class TestStartdManifests:

    def test_produces(self):
        produces = ['startd_manifests']
        s = slots.StartdManifests(config_cs)
        assert(s.produces() == produces)


    def test_acquire(self):
        s = slots.StartdManifests(config_cs)
        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file('cs.fixture')
            pprint.pprint(s.acquire())


    """
    def test_acquire_live(self):
        s = slots.StartdManifests(config_cs)
        pprint.pprint(s.acquire())
    """
