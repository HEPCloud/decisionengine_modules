# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import abc

from glideinwms.lib.xmlParse import OrderedDict


class ConfigSource(OrderedDict, metaclass=abc.ABCMeta):
    """Abstract class representing a configuration parser"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(self.load_config())

    @abc.abstractmethod
    def load_config(self) -> OrderedDict:
        """
        Reads the configuration source and returns a dictionary
        """
        raise NotImplementedError


class ConfigError(Exception):
    """Exception raised when the configuration source is invalid"""

    pass
