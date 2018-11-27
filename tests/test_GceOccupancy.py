import mock
import json
import pandas as pd

from oauth2client.client import GoogleCredentials
from googleapiclient import discovery
from decisionengine_modules.GCE.sources import GceOccupancy

config = {
    "project": "hepcloud-fnal",
    "credential" : "/etc/gwms-frontend/credentials/monitoring.json"
}

produces = ["GCE_Occupancy"]

expected_pandas_df =  pd.read_csv("GceOccupancy.output.fixture.csv")


class MockList(object):

    def execute(self):
        with open("GceOccupancy.input.fixture.json", "r") as f:
            data = json.load(f)
            return data


class MockInstances(object):

    def list(self, project, zone, pageToken):
        return MockList()


class MockClient(object):

    def instances(self):
        return MockInstances()


class TestGceOccupancy:

    def test_produces(self):
        occupancy = GceOccupancy.GceOccupancy(config)
        assert occupancy.produces() == produces

    def test_acquire(self):
        with mock.patch.object(discovery, "build") as client:
            with mock.patch.object(GceOccupancy.GceOccupancy,
                                   "get_zones") as zones:
                zones.return_value = ("us-central1-a",
                                      "us-central1-b",
                                      "us-central1-c",
                                      "us-central1-f")
                with mock.patch.object(GceOccupancy.GceOccupancy, "get_client") as client:
                    client.return_value = MockClient()
                    occupancy = GceOccupancy.GceOccupancy(config)
                    res = occupancy.acquire()
                    df = res.get(produces[0])
                    assert produces == res.keys()
                    assert expected_pandas_df.equals(res.get(produces[0]))

