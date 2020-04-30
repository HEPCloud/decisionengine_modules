import json
import os

import google.auth
import mock
import pandas as pd

from decisionengine_modules.GCE.sources import GceOccupancy

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "GceOccupancy.output.fixture.csv")
EXPECTED_DF = pd.read_csv(CSV_FILE)

CONFIG = {
    "project": "hepcloud-fnal",
    "credential": os.path.join(DATA_DIR, "monitoring.json")
}

PRODUCES = ["GCE_Occupancy"]


class MockRequest(object):

    def execute(self):
        with open(os.path.join(DATA_DIR, "GceOccupancy.input.fixture.json"), "r") as f:
            data = json.load(f)
            return data


class MockInstances(object):

    def aggregatedList(self, project):
        return MockRequest()

    def aggregatedList_next(self, previous_request, previous_response):
        return None


class MockClient(object):

    def instances(self):
        return MockInstances()


class TestGceOccupancy:

    def test_produces(self):
        with mock.patch.object(google.auth, "default") as default:
            default.return_value = (None, None)
            with mock.patch.object(GceOccupancy.GceOccupancy, "_get_client") as client:
                client.return_value = MockClient()
                occupancy = GceOccupancy.GceOccupancy(CONFIG)
                assert occupancy.produces() == PRODUCES

    def test_acquire(self):
        with mock.patch.object(google.auth, "default") as default:
            default.return_value = (None, None)
            with mock.patch.object(GceOccupancy.GceOccupancy, "_get_client") as client:
                client.return_value = MockClient()
                occupancy = GceOccupancy.GceOccupancy(CONFIG)
                res = occupancy.acquire()
                assert PRODUCES == list(res.keys())
                assert EXPECTED_DF.equals(res.get(PRODUCES[0]))
