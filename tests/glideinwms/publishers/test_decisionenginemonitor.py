import os
import pytest
import mock
import pandas
import pprint
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.glideinwms.publishers import decisionenginemonitor


config = {
    'condor_config': 'condor_config',
    'collector_host': 'fermicloud122.fnal.gov',
}

request_dict = {
    'CollectorHost': [
        'col1.com', 'col1.com', 'col1.com', 'col2.com', 'col2.com', 'col3.com'
    ],
    'GlideClientName': [
        'e1', 'e2', 'e3', 'e1', 'e2', 'e3'
    ]
}

request_df = pandas.DataFrame(request_dict)

expected_constraint = {
    'col1.com': '(glideinmytype == "glideclientmonitor") && (stringlistmember(GlideClientName, "e1,e3,e2"))',
    'col2.com': '(glideinmytype == "glideclientmonitor") && (stringlistmember(GlideClientName, "e1,e2"))',
    'col3.com': '(glideinmytype == "glideclientmonitor") && (stringlistmember(GlideClientName, "e3"))'
}

class TestDecisionEngineMonitorManifests:

    def test_consumes(self):
        consumes = ['decisionenginemonitor_manifests']
        p = decisionenginemonitor.DecisionEngineMonitorManifests(config)
        assert(p.consumes() == consumes)


    def test_publish(self):
        p = decisionenginemonitor.DecisionEngineMonitorManifests(config)
        with mock.patch.object(decisionenginemonitor.DecisionEngineMonitorManifests, 'publish_to_htcondor') as publish_to_htcondor:
            publish_to_htcondor.return_value = None
            # TODO: Complete this test when we have detailed contents of the
            #       dataframe and the logic engine facts
            assert(True == True)


    def test_create_invalidate_constraint(self):
        p = decisionenginemonitor.DecisionEngineMonitorManifests(config)
        p.create_invalidate_constraint(request_df)
        assert(p.invalidate_ads_constraint == expected_constraint)
