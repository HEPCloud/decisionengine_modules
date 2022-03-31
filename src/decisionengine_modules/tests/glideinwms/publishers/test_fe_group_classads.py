# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import pandas as pd

from decisionengine_modules.glideinwms.publishers import fe_group_classads

_CONFIG = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "collector_host": "fermicloud122.fnal.gov",
}

_REQUEST_DF = pd.DataFrame(
    {
        "CollectorHost": ["col1.com", "col1.com", "col1.com", "col2.com", "col2.com", "col3.com"],
        "ClientName": ["e1", "e2", "e3", "e1", "e2", "e3"],
        "ReqName": ["u", "v", "w", "x", "y", "z"],
    }
)


def test_consumes():
    consumes = [
        "glideclient_manifests",
        "Factory_Entries_Grid",
        "Factory_Entries_AWS",
        "Factory_Entries_GCE",
        "Factory_Entries_LCF",
    ]
    p = fe_group_classads.GlideinWMSManifests(_CONFIG)
    assert p._consumes == dict.fromkeys(consumes, pd.DataFrame)


def test_publish():
    with mock.patch.object(fe_group_classads.GlideinWMSManifests, "publish_to_htcondor", return_value=None):
        p = fe_group_classads.GlideinWMSManifests(_CONFIG)
        datablock = {
            "glideclient_manifests": _REQUEST_DF,
            "Factory_Entries_Grid": pd.DataFrame({"Name": ["u", "v", "w"]}),
            "Factory_Entries_AWS": pd.DataFrame({"Name": ["x"]}),
            "Factory_Entries_GCE": pd.DataFrame({"Name": ["y", "z"]}),
            "Factory_Entries_LCF": pd.DataFrame({"Name": []}),
            "de_logicengine_facts": pd.DataFrame(
                {
                    "fact_name": [
                        "allow_grid_requests",
                        "allow_aws_requests",
                        "allow_gce_requests",
                        "allow_lcf_requests",
                    ],
                    "fact_value": [True, False, True, False],
                }
            ),
        }
        p.publish(datablock)


def test_create_invalidate_constraint():
    p = fe_group_classads.GlideinWMSManifests(_CONFIG)
    p.create_invalidate_constraint(_REQUEST_DF)
    expected_constraint = {
        "col1.com": '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e1,e2,e3"))',
        "col2.com": '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e1,e2"))',
        "col3.com": '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e3"))',
    }
    assert p.invalidate_ads_constraint == expected_constraint
