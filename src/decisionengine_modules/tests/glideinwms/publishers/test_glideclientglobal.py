# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import pandas
import pytest

from decisionengine_modules.glideinwms.publishers import glideclientglobal

request_dict = {
    "CollectorHost": ["col1.com", "col1.com", "col1.com", "col2.com", "col2.com", "col3.com"],
    "ClientName": ["e1", "e2", "e3", "e1", "e2", "e3"],
}

request_df = pandas.DataFrame(request_dict)

expected_constraint = {
    "col1.com": '(glideinmytype == "glideclientglobal") && (stringlistmember(ClientName, "e1,e2,e3"))',
    "col2.com": '(glideinmytype == "glideclientglobal") && (stringlistmember(ClientName, "e1,e2"))',
    "col3.com": '(glideinmytype == "glideclientglobal") && (stringlistmember(ClientName, "e3"))',
}


@pytest.fixture
def global_manifests():
    config = {
        "channel_name": "test",
        "condor_config": "condor_config",
        "collector_host": "fermicloud122.fnal.gov",
    }
    return glideclientglobal.GlideClientGlobalManifests(config)


def test_consumes(global_manifests):
    assert global_manifests._consumes == {"glideclientglobal_manifests": pandas.DataFrame}


def test_publish(global_manifests):
    with mock.patch.object(global_manifests, "publish_to_htcondor", return_value=None):
        pass
        # TODO: Complete this test when we have detailed contents of the
        #       dataframe and the logic engine facts
        # assert( True == True)


def test_create_invalidate_constraint(global_manifests):
    global_manifests.create_invalidate_constraint(request_df)
    assert global_manifests.invalidate_ads_constraint == expected_constraint
