# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import os

import pytest

from decisionengine_modules.glideinwms.ConfigSource import ConfigError
from decisionengine_modules.glideinwms.DEConfigSource import DEConfigSource

GOOD_CONFIG = """{
    "glideinwms": {
        "value": "foo",
        "list": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "dict": {
            "a": 1,
            "b": 2,
            "c": 3
        }
    }
}"""

BAD_CONFIG = """{
    "foo": {
        "value": "bar"
    }
}"""

BAD_JSON = "bad json"


def test_instantiation(tmp_path):  # noqa: F811
    os.environ["CONFIG_PATH"] = str(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_text(GOOD_CONFIG)
    config = DEConfigSource(config_file)
    assert type(config) == DEConfigSource
    assert config["value"] == "foo"
    assert config["list"] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert config["dict"] == {"a": 1, "b": 2, "c": 3}


def test_config_errors(tmp_path):
    os.environ["CONFIG_PATH"] = str(tmp_path)
    config_file = tmp_path / "config.json"

    # Test missing required key
    config_file.write_text(BAD_CONFIG)
    with pytest.raises(ConfigError):
        DEConfigSource(config_file)

    # Test invalid JSON
    config_file.write_text(BAD_JSON)
    with pytest.raises(ConfigError):
        DEConfigSource(config_file)

    # Test file not found
    with pytest.raises(FileNotFoundError):
        DEConfigSource(config_file="nonexistent.json")
