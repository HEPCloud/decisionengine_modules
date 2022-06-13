# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import json
import os

from unittest import mock

import google.auth
import googleapiclient.discovery
import pandas as pd
import pytest

from decisionengine.framework.modules.Module import verify_products
from decisionengine_modules.GCE.sources import GceOccupancy

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "GceOccupancy.output.fixture.csv")
EXPECTED_DF = pd.read_csv(CSV_FILE)

CONFIG = {"channel_name": "test", "project": "hepcloud-fnal", "credential": os.path.join(DATA_DIR, "monitoring.json")}

_PRODUCES = {"GCE_Occupancy": pd.DataFrame}


class MockRequest:
    def execute(self):
        with open(os.path.join(DATA_DIR, "GceOccupancy.input.fixture.json")) as f:
            return json.load(f)


class MockInstances:
    def aggregatedList(self, project):
        return MockRequest()

    def aggregatedList_next(self, previous_request, previous_response):
        return None


class MockClient:
    def instances(self):
        return MockInstances()


@pytest.fixture
def replace_google_auth():
    with mock.patch.object(google.auth, "default", return_value=(None, None)):
        yield


def test_produces(replace_google_auth):
    assert GceOccupancy.GceOccupancy(CONFIG)._produces == _PRODUCES


def test_acquire(replace_google_auth):
    with mock.patch.object(googleapiclient.discovery, "build", return_value=MockClient()):
        occupancy = GceOccupancy.GceOccupancy(CONFIG)
        res = occupancy.acquire()
        verify_products(occupancy, res)
        assert EXPECTED_DF.equals(res.get("GCE_Occupancy"))
