import os

import mock
import pandas

from decisionengine_modules.util import testutils as utils
from decisionengine_modules.NERSC.sources import NerscAllocationInfo
from decisionengine_modules.NERSC.util import newt

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ALLOCATIONS_FIXTURE_FILE = os.path.join(
    DATA_DIR, "newt_allocations.cs.fixture")
PASSWD_FILE = os.path.join(DATA_DIR, "passwd")
FAKE_USER = "user2"

CONFIG = {
    "passwd_file": PASSWD_FILE,
    "constraints": {
       "usernames": ["timm", FAKE_USER],
       "newt_keys": {
          "rname": ["m2612", "m2696", "m2015"],
          "repo_type": ["REPO", ],
       }
    }
}

PRODUCES = ["Nersc_Allocation_Info"]
EXPECTED_PANDAS_DFRAME = pandas.DataFrame([{u'uid': 72048, u'firstname': u'Steven', u'middlename': u'C', u'projectId': 54807, u'currentAlloc': 374400000000.0, u'userAlloc': 0.0, u'repoType': u'REPO', u'repoName': u'm2612', u'lastname': u'Timm', u'userAllocPct': 2.0, u'usedAlloc': 560.0, u'name': u'timm'}])

class TestNerscAllocationInfo:

    def test_produces(self):
        nersc_allocations = NerscAllocationInfo.NerscAllocationInfo(CONFIG)
        assert nersc_allocations.produces() == PRODUCES

    def test_acquire(self):

        def side_effect_get_usage(username):
            if username == FAKE_USER:
                return {'items':[]}
            return utils.input_from_file(ALLOCATIONS_FIXTURE_FILE)

        nersc_allocations = NerscAllocationInfo.NerscAllocationInfo(CONFIG)
        with mock.patch.object(newt.Newt, "get_usage") as f:
            f.side_effect = side_effect_get_usage
            res = nersc_allocations.acquire()
            assert PRODUCES == list(res.keys())
            assert EXPECTED_PANDAS_DFRAME.equals(res[PRODUCES[0]])
