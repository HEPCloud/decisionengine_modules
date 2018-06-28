import mock
import pandas 

import utils

from decisionengine_modules.NERSC.util import newt
from decisionengine_modules.NERSC.sources import NerscAllocationInfo

config = {
    'passwd_file': 'passwd',
    'constraints': {
       'usernames': ['timm', 'user2'],
       'newt_keys': {
          'rname': ['m2612', 'm2696', 'm2015'],
          'repo_type': ["STR", ],
       }
    }
}

produces = ['Nersc_Allocation_Info']
expected_pandas_dframe = pandas.DataFrame([{u'repo_type': u'STR', u'repo_id': 45955, u'user_id': 72048, u'uid': 72048, u'resource_id': 1006, u'user_limit': 202000, u'rname': u'm2015', u'uname': u'timm', u'remain': 201943.31, u'user_percentage': 100, u'user_amount_charged': 0, u'unit_scaling': 1, u'measurement_units': u'SRU', u'rid': 61512, u'fixed': u'N', u'allocated': 202000, u'amount_charged': 56.69}, {u'repo_type': u'STR', u'repo_id': 55555, u'user_id': 72048, u'uid': 72048, u'resource_id': 1006, u'user_limit': 1000, u'rname': u'm2696', u'uname': u'timm', u'remain': 1000, u'user_percentage': 100, u'user_amount_charged': 0, u'unit_scaling': 1, u'measurement_units': u'SRU', u'rid': 72536, u'fixed': u'N', u'allocated': 1000, u'amount_charged': 0}, {u'repo_type': u'STR', u'repo_id': 45955, u'user_id': 72048, u'uid': 72048, u'resource_id': 1006, u'user_limit': 202000, u'rname': u'm2015', u'uname': u'timm', u'remain': 201943.31, u'user_percentage': 100, u'user_amount_charged': 0, u'unit_scaling': 1, u'measurement_units': u'SRU', u'rid': 61512, u'fixed': u'N', u'allocated': 202000, u'amount_charged': 56.69}, {u'repo_type': u'STR', u'repo_id': 55555, u'user_id': 72048, u'uid': 72048, u'resource_id': 1006, u'user_limit': 1000, u'rname': u'm2696', u'uname': u'timm', u'remain': 1000, u'user_percentage': 100, u'user_amount_charged': 0, u'unit_scaling': 1, u'measurement_units': u'SRU', u'rid': 72536, u'fixed': u'N', u'allocated': 1000, u'amount_charged': 0}])


class TestNerscAllocationInfo:

    def __init__(self):
        pass

    def test_produces(self):
        nersc_allocations = NerscAllocationInfo.NerscAllocationInfo(config)
        assert nersc_allocations.produces() == produces

    def test_acquire(self):
        nersc_allocations = NerscAllocationInfo.NerscAllocationInfo(config)
        with mock.patch.object(newt.Newt, 'get_usage') as f:
            f.return_value = utils.input_from_file('newt_allocations.cs.fixture')
            res = nersc_allocations.acquire()
            assert produces == res.keys()
            assert expected_pandas_dframe.equals(res[produces[0]])
