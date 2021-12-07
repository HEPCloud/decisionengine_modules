# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os
import pprint

from unittest import mock

import pandas

from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.htcondor.sources import slots
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "cs.fixture")

CONFIG = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "collector_host": "fermicloud122.fnal.gov",
}


class TestStartdManifests:
    def test_produces(self):
        s = slots.StartdManifests(CONFIG)
        assert s._produces == {"startd_manifests": pandas.DataFrame}

    def test_acquire(self):
        s = slots.StartdManifests(CONFIG)
        with mock.patch.object(htcondor_query.CondorStatus, "fetch") as f:
            f.return_value = utils.input_from_file(FIXTURE_FILE)
            pprint.pprint(s.acquire())
