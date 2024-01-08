# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import json

import pytest

from glideinwms.lib.xmlParse import OrderedDict


@pytest.fixture(scope="module")
def gwms_src_dir():
    return "/tmp/gwms_mock_dir"


@pytest.fixture(scope="module")
def gwms_module_config():
    MODULE_CONFIG = """{
        "frontend_name": "mock_frontend",
        "groups": {
            "main": {}
        },
        "security": {
            "proxy_DN": "/DC=org/DC=incommon/C=US/ST=Illinois/L=Batavia/O=Fermi Research Alliance/OU=Fermilab/CN=mock_frontend.fnal.gov"
        },
        "collectors": [
            {
                "DN": "/DC=org/DC=incommon/C=US/ST=Illinois/L=Batavia/O=Fermi Research Alliance/OU=Fermilab/CN=mock_collector.fnal.gov",
                "group": "default",
                "node": "mock_collector.fnal.gov:9618",
                "secondary": "False"
            }
        ]
    }"""

    return json.loads(MODULE_CONFIG, object_hook=OrderedDict)


@pytest.fixture(scope="module")
def gwms_module_invalid_config():
    MODULE_INVALID_CONFIG = """{
        "frontend_name": "mock_frontend",
        "invalid_key": "test_value"
    }"""

    return json.loads(MODULE_INVALID_CONFIG, object_hook=OrderedDict)
