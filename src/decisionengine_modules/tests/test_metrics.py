# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import json
import os

from unittest import mock

import pandas
import pytest

from decisionengine_modules.htcondor import htcondor_query
from decisionengine_modules.htcondor.sources import source
from decisionengine_modules.htcondor.sources.source import (
    DEM_HTCONDOR_CORES_COUNT,
    DEM_HTCONDOR_MEMORY_COUNT,
    DEM_HTCONDOR_SLOTS_STATUS_COUNT,
)
from decisionengine_modules.util import testutils as utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "cs.fixture")
EXPECTED_VALUES_FILE = os.path.join(DATA_DIR, "expected_values.json")


@pytest.fixture
def source_instance():
    config = {
        "channel_name": "test",
        "condor_config": "condor_config",
        "collector_host": "fermicloud122.fnal.gov",
        "classad_attrs": ["ClusterId", "ProcId", "JobStatus"],
        "group_attr": ["Name"],
        "subsystem_name": "subsystem_name",
        "correction_map": "correction_map",
    }
    return source.ResourceManifests(config)


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
        for label, expected_value in expected_values["Slots"].items():
            metric_value = DEM_HTCONDOR_SLOTS_STATUS_COUNT.labels(label)._value.get()
            assert metric_value == expected_value


# @pytest.mark.unit
def test_count_cores(source_instance, setup_metrics_dir_for_test):
    expected_values = load_expected_values()
    with mock.patch.object(htcondor_query.CondorStatus, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        source_instance.load()
        for label, expected_value in expected_values["Cores"].items():
            metric_value = DEM_HTCONDOR_CORES_COUNT.labels(label)._value.get()
            assert metric_value == expected_value


# @pytest.mark.unit
def test_count_memory(source_instance, setup_metrics_dir_for_test):
    expected_values = load_expected_values()
    with mock.patch.object(htcondor_query.CondorStatus, "fetch", return_value=utils.input_from_file(FIXTURE_FILE)):
        source_instance.load()
        for label, expected_value in expected_values["Memory"].items():
            metric_value = DEM_HTCONDOR_MEMORY_COUNT.labels(label)._value.get()
            assert metric_value == expected_value
