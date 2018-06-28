import mock
import pandas

import utils

from decisionengine_modules.NERSC.util import newt
from decisionengine_modules.NERSC.sources import NerscJobInfo

config = {
    'passwd_file': 'passwd',
    'constraints': {
       'machines': ["edison", "cori"],
       'newt_keys': {
          'user': ["hufnagel", "timm"],
          'repo': ['m2612', 'm2696'],
       }
    }
}

produces = ['Nersc_Job_Info']

"""
expected correctly filtered results
"""

with open("newt_jobs.cs.test.fixture", "r") as f:
    d = eval(f.read())

expected_pandas_dframe = pandas.DataFrame(d)


class TestNerscJobInfo:

    def __init__(self):
        pass

    def test_produces(self):
        nersc_job_info = NerscJobInfo.NerscJobInfo(config)
        assert nersc_job_info.produces() == produces

    def test_acquire(self):
        nersc_job_info = NerscJobInfo.NerscJobInfo(config)

        with mock.patch.object(newt.Newt, 'get_status') as get_status:
            get_status.return_value = utils.input_from_file('newt_status.cs.fixture')
            with mock.patch.object(newt.Newt, 'get_queue') as get_queue:
                get_queue.return_value = utils.input_from_file('newt_jobs.cs.fixture')
                res = nersc_job_info.acquire()
                assert produces == res.keys()
                assert expected_pandas_dframe.equals(res[produces[0]])
