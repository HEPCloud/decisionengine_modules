# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import json
import os

from unittest import mock

import pandas
import pytest

from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.htcondor.sources import source
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "cs.fixture")
EXPECTED_VALUES_FILE = os.path.join(DATA_DIR, "expected_metric_values.json")


class MockResourceManifests(source.ResourceManifests):
    def acquire(self):
        return pandas.DataFrame()


@pytest.fixture
def source_instance():
    config = {
        "channel_name": "test",
        "condor_config": "condor_config",
        "collector_host": "fermicloud122.fnal.gov",
        "classad_attrs": ["ClusterId", "ProcId", "JobStatus"],
        "group_attr": ["Name"],
        "subsystem_name": "subsystem_name",
        "correction_map": {
            "Activity": "",
            "Cpus": 0,
            "GLIDECLIENT_NAME": "",
            "GLIDEIN_CredentialIdentifier": "",
            "GLIDEIN_Entry_Name": "",
            "GLIDEIN_FACTORY": "",
            "GLIDEIN_GridType": "",
            "GLIDEIN_Name": "",
            "GLIDEIN_Resource_Slots": "",
            "Memory": 0,
            "PartitionableSlot": 0,
            "SlotType": "",
            "State": "",
            "TotalCpus": 0,
            "TotalSlotCpus": 0,
            "TotalSlots": 0,
        },
    }
    return MockResourceManifests(config)


@pytest.fixture
def setup_metrics_dir_for_test(monkeypatch, tmp_path):
    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", tmp_path)


def load_expected_values():
    with open(EXPECTED_VALUES_FILE) as f:
        return json.load(f)


# @pytest.mark.unit
def test_count_slots(source_instance, setup_metrics_dir_for_test):
    expected_values = load_expected_values()
    with mock.patch.object(htcondor_query.CondorStatus, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        source_instance.load()
        metric_values = source_instance.get_metric_values()["slots_status_count"]
        for label, expected_value in expected_values["Slots"].items():
            assert expected_value == 0 or metric_values[label] == expected_value


# @pytest.mark.unit
def test_count_cores(source_instance, setup_metrics_dir_for_test):
    expected_values = load_expected_values()
    with mock.patch.object(htcondor_query.CondorStatus, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        source_instance.load()
        metric_values = source_instance.get_metric_values()["cores_count"]
        for label, expected_value in expected_values["Cores"].items():
            assert expected_value == 0 or metric_values[label] == expected_value


# @pytest.mark.unit
def test_count_memory(source_instance, setup_metrics_dir_for_test):
    expected_values = load_expected_values()
    with mock.patch.object(htcondor_query.CondorStatus, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        source_instance.load()
        metric_values = source_instance.get_metric_values()["memory_count"]
        for label, expected_value in expected_values["Memory"].items():
            assert expected_value == 0 or metric_values[label] == expected_value
