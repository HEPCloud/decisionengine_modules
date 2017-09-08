import pytest
import mock
import pprint
import utils
from decisionengine.modules.NERSC.sources import newt_query
from decisionengine.modules.NERSC.sources import nersc_allocation_info

config_cs = {

    'renew_cookie_script' : 'root/renew_cookies.sh',
    'cookie_file' : '../NERSC/newt_cookies.txt',
    'constraints' : {
        'repo_types' : ["REPO"],
        'repo_names' : ["m2696", "m2612"],
        'usernames': ["hufnagel", "timm"]
    },
}

class TestNerscAllocationInfo:

    def test_produces(self):
        produces = ['Nersc_Allocation_Info']
        nersc_allocations = nersc_allocation_info.NERSCAllocationInfo(config_cs)
        assert nersc_allocations.produces() == produces


    def test_acquire(self):
        nersc_allocations = nersc_allocation_info.NERSCAllocationInfo(config_cs)
        with mock.patch.object(newt_query.NewtQuery, 'send_query') as f:
            f.return_value = utils.input_from_file('newt_allocations.cs.fixture')
            pprint.pprint(nersc_allocations.acquire())

    def test_acquire_live(self):
        nersc_allocations = nersc_allocation_info.NERSCAllocationInfo(config_cs)
        pprint.pprint(nersc_allocations.acquire())




