# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import copy

from unittest import mock

import pandas as pd

from decisionengine_modules.glideinwms.publishers import fe_group_classads

_CONFIG = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "collector_host": "fermicloud122.fnal.gov",
    "queries": {
        "Grid": "@requests.ClientName != 'e1' and @entries.Other % 2 != 0",
        "AWS": "@requests.CollectorHost == 'col2.com'",
        "GCE": "@requests.CollectorHost == 'col3.com'",
    },
}

_REQUEST_DICT = {
    "CollectorHost": ["col1.com", "col1.com", "col1.com", "col2.com", "col2.com", "col3.com"],
    "ClientName": ["e1", "e2", "e3", "e1", "e2", "e3"],
    "ReqName": ["u", "v", "w", "x", "y", "z"],
    "ReqIdleGlideins": 1,
}

_REQUEST_DF = pd.DataFrame(_REQUEST_DICT)


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
    with mock.patch.object(
        fe_group_classads.GlideinWMSManifests, "publish_to_htcondor", return_value=None
    ) as publish_to_condor:
        p = fe_group_classads.GlideinWMSManifests(_CONFIG)
        datablock = {
            "glideclient_manifests": _REQUEST_DF,
            "Factory_Entries_Grid": pd.DataFrame({"Name": ["u", "v", "w"], "Other": [1, 2, 3]}),
            "Factory_Entries_AWS": pd.DataFrame({"Name": ["x"], "Other": 5}),
            "Factory_Entries_GCE": pd.DataFrame({"Name": ["y", "z"], "Other": 7}),
            "Factory_Entries_LCF": pd.DataFrame({"Name": [], "Other": 9}),
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

        expected_dict = copy.deepcopy(_REQUEST_DICT)
        expected_dict["ReqIdleGlideins"] = [0, 0, 1, 0, 0, 1]
        actual_classad_type, actual_df = publish_to_condor.call_args[0]
        expected_df = pd.DataFrame(expected_dict).reindex_like(actual_df)
        assert actual_classad_type == "glideclient"
        assert actual_df.compare(expected_df).empty


def test_create_invalidate_constraint():
    p = fe_group_classads.GlideinWMSManifests(_CONFIG)
    p.create_invalidate_constraint(_REQUEST_DF)
    expected_constraint = {
        "col1.com": '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e1,e2,e3"))',
        "col2.com": '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e1,e2"))',
        "col3.com": '(glideinmytype == "glideclient") && (stringlistmember(ClientName, "e3"))',
    }
    assert p.invalidate_ads_constraint == expected_constraint
