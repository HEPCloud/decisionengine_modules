import os

import mock
import pandas

from decisionengine_modules.util import testutils as utils
from decisionengine_modules.NERSC.sources import NerscAllocationInfo
from decisionengine_modules.NERSC.util import newt

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ALLOCATIONS_FIXTURE_FILE = os.path.join(DATA_DIR, "newt_allocations.cs.fixture")
PASSWD_FILE = os.path.join(DATA_DIR, "passwd")

CONFIG = {
    "passwd_file": PASSWD_FILE,
    "constraints": {
       "usernames": ["timm", "user2"],
       "newt_keys": {
          "rname": ["m2612", "m2696", "m2015"],
          "repo_type": ["STR", ],
       }
    }
}

PRODUCES = ["Nersc_Allocation_Info"]
EXPECTED_PANDAS_DFRAME = pandas.DataFrame([{u'repo_type': u'STR', u'repo_id': 45955, u'user_id': 72048, u'uid': 72048, u'resource_id': 1006, u'user_limit': 202000, u'rname': u'm2015', u'uname': u'timm', u'remain': 201943.31, u'user_percentage': 100, u'user_amount_charged': 0, u'unit_scaling': 1, u'measurement_units': u'SRU', u'rid': 61512, u'fixed': u'N', u'allocated': 202000, u'amount_charged': 56.69}, {u'repo_type': u'STR', u'repo_id': 55555, u'user_id': 72048, u'uid': 72048, u'resource_id': 1006, u'user_limit': 1000, u'rname': u'm2696', u'uname': u'timm', u'remain': 1000, u'user_percentage': 100, u'user_amount_charged': 0, u'unit_scaling': 1, u'measurement_units': u'SRU', u'rid': 72536, u'fixed': u'N', u'allocated': 1000, u'amount_charged': 0}, {u'repo_type': u'STR', u'repo_id': 45955, u'user_id': 72048, u'uid': 72048, u'resource_id': 1006, u'user_limit': 202000, u'rname': u'm2015', u'uname': u'timm', u'remain': 201943.31, u'user_percentage': 100, u'user_amount_charged': 0, u'unit_scaling': 1, u'measurement_units': u'SRU', u'rid': 61512, u'fixed': u'N', u'allocated': 202000, u'amount_charged': 56.69}, {u'repo_type': u'STR', u'repo_id': 55555, u'user_id': 72048, u'uid': 72048, u'resource_id': 1006, u'user_limit': 1000, u'rname': u'm2696', u'uname': u'timm', u'remain': 1000, u'user_percentage': 100, u'user_amount_charged': 0, u'unit_scaling': 1, u'measurement_units': u'SRU', u'rid': 72536, u'fixed': u'N', u'allocated': 1000, u'amount_charged': 0}])


class TestNerscAllocationInfo:

    def test_produces(self):
        nersc_allocations = NerscAllocationInfo.NerscAllocationInfo(CONFIG)
        assert nersc_allocations.produces() == PRODUCES

    def test_acquire(self):
        nersc_allocations = NerscAllocationInfo.NerscAllocationInfo(CONFIG)
        with mock.patch.object(newt.Newt, "get_usage") as f:
            f.return_value = utils.input_from_file(ALLOCATIONS_FIXTURE_FILE)
            res = nersc_allocations.acquire()
            assert PRODUCES == list(res.keys())
            assert EXPECTED_PANDAS_DFRAME.equals(res[PRODUCES[0]])
