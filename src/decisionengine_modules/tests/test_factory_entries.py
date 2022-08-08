# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os
import pprint
import time

from unittest import mock

import pandas as pd

from decisionengine_modules.glideinwms.sources import factory_entries
from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "factory_entries.cs.fixture")

CONFIG_FACTORY_ENTRIES = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "factories": [
        {
            "collector_host": "cmssrv280.fnal.gov",
        },
    ],
}

CONFIG_FACTORY_ENTRIES_BAD = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "factories": [
        {
            "collector_host": "dummy_collector.fnal.gov",
        },
    ],
}

CONFIG_FACTORY_ENTRIES_BAD_WITH_TIMEOUT = {
    "channel_name": "test",
    "condor_config": "condor_config",
    "max_retries": 2,
    "retry_interval": 2,
    "factories": [
        {
            "collector_host": "dummy_collector.fnal.gov",
        },
    ],
}

CONFIG_FACTORY_ENTRIES_CORMAP = {
    "channel_name": "test",
    "condor_config": "/etc/condor/condor_config",
    "factories": [
        {
            "collector_host": "dummy_collector.fnal.gov",
            "classad_attrs": ["GLIDEIN_GridType", "GLIDEIN_CMSSite", "GLIDEIN_Resource_Slots"],
            "correction_map": {"GLIDEIN_Resource_Slots": "DummySlots", "GLIDEIN_CMSSite": "DummySite"},
        },
    ],
}


def test_produces():
    entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES)
    assert entries._produces == {"Factory_Entries": pd.DataFrame}


def test_acquire():
    entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES)
    with mock.patch.object(htcondor_query.CondorStatus, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        pprint.pprint(entries.acquire())


def test_acquire_live():
    entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES)
    pprint.pprint(entries.acquire())


def test_acquire_bad():
    entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES_BAD)
    result = entries.acquire()
    for df in result.values():
        assert df.dropna().empty


def test_acquire_bad_with_timeout():
    entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES_BAD_WITH_TIMEOUT)
    start = time.time()
    result = entries.acquire()
    end = time.time()
    # Set by tuning max_retries and the retry_interval
    assert end - start > 5
    for df in result.values():
        assert df.dropna().empty


def test_acquire_correctionmap():
    df1 = pd.DataFrame(data={"GLIDEIN_Resource_Slots": ["DummySlots", "DummySlots"]})
    df2 = pd.DataFrame(data={"GLIDEIN_CMSSite": ["DummySite", "DummySite"]})

    entries = factory_entries.FactoryEntries(CONFIG_FACTORY_ENTRIES_CORMAP)
    with mock.patch.object(htcondor_query.CondorStatus, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        all_entries = entries.acquire()
        dummypd = all_entries["Factory_Entries"].xs("Grid")
        assert df1.equals(dummypd[["GLIDEIN_Resource_Slots"]])
        assert df2.equals(dummypd[["GLIDEIN_CMSSite"]])
