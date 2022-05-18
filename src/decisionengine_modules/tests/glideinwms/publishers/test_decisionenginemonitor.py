# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import pandas

from decisionengine_modules.glideinwms.publishers import decisionenginemonitor

config = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "collector_host": "fermicloud122.fnal.gov",
}

request_dict = {
    "CollectorHost": ["col1.com", "col1.com", "col1.com", "col2.com", "col2.com", "col3.com"],
    "GlideClientName": ["e1", "e2", "e3", "e1", "e2", "e3"],
}

request_df = pandas.DataFrame(request_dict)

expected_constraint = {
    "col1.com": '(glideinmytype == "glideclientmonitor") && (stringlistmember(GlideClientName, "e1,e2,e3"))',
    "col2.com": '(glideinmytype == "glideclientmonitor") && (stringlistmember(GlideClientName, "e1,e2"))',
    "col3.com": '(glideinmytype == "glideclientmonitor") && (stringlistmember(GlideClientName, "e3"))',
}


def test_consumes():
    p = decisionenginemonitor.DecisionEngineMonitorManifests(config)
    assert p._consumes == {"decisionenginemonitor_manifests": pandas.DataFrame}


def test_publish():
    decisionenginemonitor.DecisionEngineMonitorManifests(config)
    with mock.patch.object(
        decisionenginemonitor.DecisionEngineMonitorManifests, "publish_to_htcondor"
    ) as publish_to_htcondor:
        publish_to_htcondor.return_value = None
        # TODO: Complete this test when we have detailed contents of the
        #       dataframe and the logic engine facts
        # assert(True == True)


def test_create_invalidate_constraint():
    p = decisionenginemonitor.DecisionEngineMonitorManifests(config)
    p.create_invalidate_constraint(request_df)
    assert p.invalidate_ads_constraint == expected_constraint
