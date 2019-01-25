import mock
import json
import pandas as pd

from googleapiclient import discovery
from decisionengine_modules.GCE.sources import GceOccupancy

config = {
    "project": "hepcloud-fnal",
    "credential": "/etc/gwms-frontend/credentials/monitoring.json"
}

produces = ["GCE_Occupancy"]

expected_pandas_df = pd.read_csv("GceOccupancy.output.fixture.csv")


class MockRequest(object):    

    def execute(self):
        with open("GceOccupancy.input.fixture.json", "r") as f:
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
        occupancy = GceOccupancy.GceOccupancy(config)
        assert occupancy.produces() == produces

    def test_acquire(self):
        with mock.patch.object(discovery, "build") as client:
                with mock.patch.object(GceOccupancy.GceOccupancy, "_get_client") as client:
                    client.return_value = MockClient()
                    occupancy = GceOccupancy.GceOccupancy(config)
                    res = occupancy.acquire()
                    assert produces == res.keys()
                    assert expected_pandas_df.equals(res.get(produces[0]))
