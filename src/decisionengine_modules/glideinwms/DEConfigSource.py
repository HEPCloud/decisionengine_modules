# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import json

from glideinwms.lib.xmlParse import OrderedDict

from decisionengine.framework.engine import de_client
from decisionengine_modules.glideinwms.ConfigSource import ConfigError, ConfigSource


class DEConfigSource(ConfigSource):
    """
    Handles HEPCloud Decision Engine configuration source.
    """

    def __init__(self, host="localhost", port="8888"):
        self.host = host
        self.port = port
        super().__init__()

    def load_config(self):
        try:
            de_config = de_client.main(["--port", self.port, "--host", self.host, "--show-de-config"], logger_name=None)
            de_config = json.loads(de_config, object_hook=OrderedDict)["glideinwms"]
            return de_config
        except Exception as e:
            raise ConfigError(f"Failed to load HEPCloud Decision Engine configuration: {e}")
