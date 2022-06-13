# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

from unittest import mock

import pandas
import pytest

from decisionengine.framework.modules.Module import verify_products
from decisionengine_modules.NERSC.sources import NerscAllocationInfo
from decisionengine_modules.NERSC.util import newt
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ALLOCATIONS_FIXTURE_FILE = os.path.join(DATA_DIR, "newt_allocations.cs.fixture")
PASSWD_FILE = os.path.join(DATA_DIR, "passwd")
FAKE_USER = "user2"

_PRODUCES = {"Nersc_Allocation_Info": pandas.DataFrame}
EXPECTED_PANDAS_DFRAME = pandas.DataFrame(
    [
        {
            "uid": 72048,
            "firstname": "Steven",
            "middlename": "C",
            "projectId": 54807,
            "currentAlloc": 374400000000.0,
            "userAlloc": 0.0,
            "repoType": "REPO",
            "repoName": "m2612",
            "lastname": "Timm",
            "userAllocPct": 2.0,
            "usedAlloc": 560.0,
            "name": "timm",
        }
    ]
)


@pytest.fixture
def nersc_allocations():
    config = {
        "channel_name": "test",
        "passwd_file": PASSWD_FILE,
        "constraints": {
            "usernames": ["timm", FAKE_USER],
            "newt_keys": {
                "rname": ["m2612", "m2696", "m2015"],
                "repo_type": [
                    "REPO",
                ],
            },
        },
    }
    return NerscAllocationInfo.NerscAllocationInfo(config)


def test_produces(nersc_allocations):
    assert nersc_allocations._produces == _PRODUCES


def test_acquire(nersc_allocations):
    def side_effect_get_usage(username):
        if username == FAKE_USER:
            return {"items": []}
        return utils.input_from_file(ALLOCATIONS_FIXTURE_FILE)

    with mock.patch.object(newt.Newt, "get_usage", side_effect=side_effect_get_usage):
        res = nersc_allocations.acquire()
        verify_products(nersc_allocations, res)
        assert EXPECTED_PANDAS_DFRAME.equals(res["Nersc_Allocation_Info"])
