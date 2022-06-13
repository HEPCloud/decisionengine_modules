# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pytest

from decisionengine_modules.glideinwms.ConfigSource import ConfigError
from decisionengine_modules.glideinwms.DEConfigSource import DEConfigSource
from decisionengine_modules.glideinwms.tests.fixtures import de_client_config  # noqa: F401


def test_instantiation(de_client_config):  # noqa: F811
    with de_client_config:
        config = DEConfigSource()
        assert config["value"] == "foo"


def test_config_error():
    with pytest.raises(ConfigError):
        DEConfigSource()
