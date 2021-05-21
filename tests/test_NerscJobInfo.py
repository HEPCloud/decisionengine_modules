import os

import mock
import pandas

from decisionengine_modules.util import testutils as utils
from decisionengine_modules.NERSC.sources import NerscJobInfo
from decisionengine_modules.NERSC.util import newt
from decisionengine.framework.modules.Module import verify_products

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEST_FIXTURE_FILE = os.path.join(DATA_DIR, "newt_jobs.cs.test.fixture")
PASSWD_FILE = os.path.join(DATA_DIR, "passwd")

CONFIG = {
    "passwd_file": PASSWD_FILE,
    "constraints": {
        "machines": ["edison", "cori"],
        "newt_keys": {
            "user": ["hufnagel", "timm"],
            "repo": ["m2612", "m2696"],
        }
    }
}

_PRODUCES = {"Nersc_Job_Info": pandas.DataFrame}

"""
expected correctly filtered results
"""

with open(TEST_FIXTURE_FILE, "r") as f:
    d = eval(f.read())

EXPECTED_PANDAS_DFRAME = pandas.DataFrame(d)

STATUS_FIXTURE_FILE = os.path.join(DATA_DIR, "newt_status.cs.fixture")
JOBS_FIXTURE_FILE = os.path.join(DATA_DIR, "newt_jobs.cs.fixture")


class TestNerscJobInfo:

    def test_produces(self):
        nersc_job_info = NerscJobInfo.NerscJobInfo(CONFIG)
        assert nersc_job_info._produces == _PRODUCES

    def test_acquire(self):
        nersc_job_info = NerscJobInfo.NerscJobInfo(CONFIG)
        with mock.patch.object(newt.Newt, "get_status") as get_status:
            get_status.return_value = utils.input_from_file(
                STATUS_FIXTURE_FILE)
            with mock.patch.object(newt.Newt, "get_queue") as get_queue:
                get_queue.return_value = utils.input_from_file(
                    JOBS_FIXTURE_FILE)
                res = nersc_job_info.acquire()
                verify_products(nersc_job_info, res)
                new_df = res['Nersc_Job_Info']
                new_df = new_df.reindex(EXPECTED_PANDAS_DFRAME.columns, axis=1)
                pandas.testing.assert_frame_equal(EXPECTED_PANDAS_DFRAME, new_df)
