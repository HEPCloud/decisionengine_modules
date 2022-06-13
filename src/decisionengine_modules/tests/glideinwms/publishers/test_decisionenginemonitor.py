# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import pandas
import pytest

from decisionengine_modules.glideinwms.publishers import decisionenginemonitor

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


@pytest.fixture
def de_monitor():
    config = {
        "channel_name": "test",
        "condor_config": "condor_config",
        "collector_host": "fermicloud122.fnal.gov",
    }
    return decisionenginemonitor.DecisionEngineMonitorManifests(config)


def test_consumes(de_monitor):
    assert de_monitor._consumes == {"decisionenginemonitor_manifests": pandas.DataFrame}


def test_publish(de_monitor):
    with mock.patch.object(de_monitor, "publish_to_htcondor", return_value=None):
        pass
        # TODO: Complete this test when we have detailed contents of the
        #       dataframe and the logic engine facts
        # assert(True == True)


def test_create_invalidate_constraint(de_monitor):
    de_monitor.create_invalidate_constraint(request_df)
    assert de_monitor.invalidate_ads_constraint == expected_constraint
