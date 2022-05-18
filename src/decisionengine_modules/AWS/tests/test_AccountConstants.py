# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

from decisionengine_modules.AWS.sources import DEAccountContants

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SAMPLE_FILE = os.path.join(DATA_DIR, "AccountConstants_sample.py")


def test_load():
    account_dict = DEAccountContants.load_constants(SAMPLE_FILE)
    assert account_dict is not None
