import os
import pytest
import mock
import pandas
import pprint
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.glideinwms.publishers import fe_group_classads


config = {
    'condor_config': 'condor_config',
    'collector_host': 'fermicloud122.fnal.gov',
}

request_dict = {
    'CollectorHost': [
        'col1.com', 'col1.com', 'col1.com', 'col2.com', 'col2.com', 'col3.com'
    ],
    'ClientName': [
        'e1', 'e2', 'e3', 'e1', 'e2', 'e3'
    ]
}

request_df = pandas.DataFrame(request_dict)

expected_constraint = {
    'col1.com': '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e1,e2,e3"))',
    'col2.com': '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e1,e2"))',
    'col3.com': '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e3"))'
}

class TestGlideinWMSManifests:

    def test_consumes(self):
        consumes = ['glideclient_manifests', 'Factory_Entries_Grid', 'Factory_Entries_AWS', 'Factory_Entries_GCE', 'Factory_Entries_LCF']
        p = fe_group_classads.GlideinWMSManifests(config)
        assert(p.consumes() == consumes)


    def test_publish(self):
        p = fe_group_classads.GlideinWMSManifests(config)
        with mock.patch.object(fe_group_classads.GlideinWMSManifests, 'publish_to_htcondor') as publish_to_htcondor:
            publish_to_htcondor.return_value = None
            # TODO: Complete this test when we have detailed contents of the
            #       dataframe and the logic engine facts
            assert(True == True)


    def test_create_invalidate_constraint(self):
        p = fe_group_classads.GlideinWMSManifests(config)
        p.create_invalidate_constraint(request_df)
        assert(p.invalidate_ads_constraint == expected_constraint)
