# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os
import pprint

from unittest import mock

import pandas
import pytest

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


@pytest.fixture
def factory_client_instance():
    return factory_client.FactoryClientManifests(CONFIG)


def test_produces(factory_client_instance):
    assert factory_client_instance._produces == {"factoryclient_manifests": pandas.DataFrame}


def test_acquire(factory_client_instance):
    with mock.patch.object(htcondor_query.CondorStatus, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        pprint.pprint(factory_client_instance.acquire())


def test_acquire_live(factory_client_instance):
    pprint.pprint(factory_client_instance.acquire())


def test_acquire_bad():
    fc = factory_client.FactoryClientManifests(CONFIG_BAD)
    fc_df = fc.acquire()
    assert len(fc_df["factoryclient_manifests"]) == 0
