# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import json
import os

from glideinwms.lib.xmlParse import OrderedDict

from decisionengine.framework.config.policies import global_config_dir, GLOBAL_CONFIG_FILENAME
from decisionengine.framework.config.ValidConfig import ValidConfig
from decisionengine_modules.glideinwms.ConfigSource import ConfigError, ConfigSource


class DEConfigSource(ConfigSource):
    """
    Handles HEPCloud Decision Engine configuration source.
    """

    def __init__(self, config_file=GLOBAL_CONFIG_FILENAME):
        self.config_file = os.path.join(global_config_dir(), config_file)
        super().__init__()

    def load_config(self):
        try:
            return json.loads(json.dumps(ValidConfig(self.config_file)["glideinwms"]), object_hook=OrderedDict)
        except KeyError as e:
            raise ConfigError(
                f"Could not find the required configuration key '{e}' in the Decision Engine configuration ({self.config_file})."
            )
        except RuntimeError as e:
            raise ConfigError(f"Could not load the Decision Engine configuration ({self.config_file}): {e}") from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Could not find the Decision Engine configuration ({self.config_file}).") from e
