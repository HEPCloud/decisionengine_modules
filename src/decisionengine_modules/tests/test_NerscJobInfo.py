# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

from unittest import mock

import pandas as pd
import pytest

from decisionengine.framework.modules.Module import verify_products
from decisionengine_modules.NERSC.sources import NerscJobInfo
from decisionengine_modules.NERSC.util import newt
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEST_FIXTURE_FILE = os.path.join(DATA_DIR, "newt_jobs.cs.test.fixture")
PASSWD_FILE = os.path.join(DATA_DIR, "passwd")

_PRODUCES = {"Nersc_Job_Info": pd.DataFrame}

# expected correctly filtered results

with open(TEST_FIXTURE_FILE) as f:
    d = eval(f.read())

EXPECTED_PANDAS_DFRAME = pd.DataFrame(d)

STATUS_FIXTURE_FILE = os.path.join(DATA_DIR, "newt_status.cs.fixture")
JOBS_FIXTURE_FILE = os.path.join(DATA_DIR, "newt_jobs.cs.fixture")


@pytest.fixture
def nersc_job_info():
    config = {
        "channel_name": "test",
        "passwd_file": PASSWD_FILE,
        "constraints": {
            "machines": ["edison", "cori"],
            "newt_keys": {
                "user": ["hufnagel", "timm"],
                "repo": ["m2612", "m2696"],
            },
        },
    }
    return NerscJobInfo.NerscJobInfo(config, logger=None)


def test_produces(nersc_job_info):
    assert nersc_job_info._produces == _PRODUCES


def test_acquire(nersc_job_info):
    with mock.patch.object(
        newt.Newt, "get_status", return_value=utils.input_from_file(STATUS_FIXTURE_FILE)
    ), mock.patch.object(newt.Newt, "get_queue", return_value=utils.input_from_file(JOBS_FIXTURE_FILE)):
        res = nersc_job_info.acquire()
        verify_products(nersc_job_info, res)
        new_df = res["Nersc_Job_Info"]
        new_df = new_df.reindex(EXPECTED_PANDAS_DFRAME.columns, axis=1)
        pd.testing.assert_frame_equal(EXPECTED_PANDAS_DFRAME, new_df)
