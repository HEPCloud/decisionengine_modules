import pytest
import mock
import pprint
import utils
from decisionengine_modules.NERSC.util import newt
from decisionengine_modules.NERSC.sources import NerscJobInfo

config = {
    'passwd_file' : 'passwd',
    'constraints' : {
       'machines': ["edison", "cori"],
       'newt_keys' : {
          'user': ["hufnagel", "timm"],
          'repo': ['m2612','m2696'],
       }
    }
}

class TestNerscJobInfo:

    def test_produces(self):
        produces = ['Nersc_Job_Info']
        nersc_job_info = NerscJobInfo.NerscJobInfo(config)
        assert nersc_job_info.produces() == produces

    def test_acquire(self):
        nersc_job_info = NerscJobInfo.NerscJobInfo(config)

        with mock.patch.object(newt.Newt, 'get_status') as f:
            f.return_value = utils.input_from_file('newt_status.cs.fixture')
            print f.return_value, type(f.return_value)
            with mock.patch.object(newt.Newt, 'get_queue') as f1:
                f1.return_value = utils.input_from_file('newt_jobs.cs.fixture')
                pprint.pprint(nersc_job_info.acquire())
