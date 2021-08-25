import pandas

from unittest import mock

from decisionengine_modules.glideinwms.publishers import glideclientglobal


config = {
    'channel_name': 'test',
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
    'col1.com': '(glideinmytype == "glideclientglobal") && (stringlistmember(ClientName, "e1,e2,e3"))',
    'col2.com': '(glideinmytype == "glideclientglobal") && (stringlistmember(ClientName, "e1,e2"))',
    'col3.com': '(glideinmytype == "glideclientglobal") && (stringlistmember(ClientName, "e3"))'
}


class TestGlideClientGlobalManifests:

    def test_consumes(self):
        p = glideclientglobal.GlideClientGlobalManifests(config)
        assert p._consumes == {'glideclientglobal_manifests': pandas.DataFrame}

    def test_publish(self):
        glideclientglobal.GlideClientGlobalManifests(config)
        with mock.patch.object(glideclientglobal.GlideClientGlobalManifests, 'publish_to_htcondor') as publish_to_htcondor:
            publish_to_htcondor.return_value = None
            # TODO: Complete this test when we have detailed contents of the
            #       dataframe and the logic engine facts
            #assert( True == True)

    def test_create_invalidate_constraint(self):
        p = glideclientglobal.GlideClientGlobalManifests(config)
        p.create_invalidate_constraint(request_df)
        assert p.invalidate_ads_constraint == expected_constraint
