import pytest
import mock
import pprint
import utils
from decisionengine_modules.NERSC.util import newt
from decisionengine_modules.NERSC.sources import NerscAllocationInfo

config = {
    'passwd_file' : 'passwd',
    'constraints': {
       'usernames': [ 'timm', 'user2' ],
       'newt_keys' : {
          'rname': ['m2612', 'm2696', 'm2015'],
          'repo_type': ["STR",],
       }
    }
}

class TestNerscAllocationInfo:

    def test_produces(self):
        produces = ['Nersc_Allocation_Info']
        nersc_allocations = NerscAllocationInfo.NerscAllocationInfo(config)
        assert nersc_allocations.produces() == produces
        assert produces == produces

    def test_acquire(self):
        nersc_allocations = NerscAllocationInfo.NerscAllocationInfo(config)
        with mock.patch.object(newt.Newt, 'get_usage') as f:
            f.return_value = utils.input_from_file('newt_allocations.cs.fixture')
            pprint.pprint(nersc_allocations.acquire())

