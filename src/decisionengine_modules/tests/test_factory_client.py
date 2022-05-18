# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os
import pprint

from unittest import mock

import pandas

from decisionengine_modules.glideinwms.sources import factory_client
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "factory_client.cs.fixture")

CONFIG = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "collector_host": "cmssrv280.fnal.gov",
}

CONFIG_BAD = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "collector_host": "dummy_collector.fnal.gov",
}


def test_produces():
    fc = factory_client.FactoryClientManifests(CONFIG)
    assert fc._produces == {"factoryclient_manifests": pandas.DataFrame}


def test_acquire():
    fc = factory_client.FactoryClientManifests(CONFIG)
    with mock.patch.object(htcondor_query.CondorStatus, "fetch") as f:
        f.return_value = utils.input_from_file(FIXTURE_FILE)
        pprint.pprint(fc.acquire())


def test_acquire_live():
    fc = factory_client.FactoryClientManifests(CONFIG)
    pprint.pprint(fc.acquire())


def test_acquire_bad():
    fc = factory_client.FactoryClientManifests(CONFIG_BAD)
    fc_df = fc.acquire()
    assert len(fc_df["factoryclient_manifests"]) == 0
