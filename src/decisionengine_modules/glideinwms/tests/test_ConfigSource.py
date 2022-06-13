# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pytest

from decisionengine_modules.glideinwms.ConfigSource import ConfigSource


def test_abstract_instantiation():
    with pytest.raises(NotImplementedError):
        ConfigSource()
