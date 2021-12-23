# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from decisionengine_modules.glideinwms.ConfigSource import ConfigSource


def test_abstract_instantiation():
    try:
        ConfigSource()
    except Exception as e:
        assert isinstance(e, NotImplementedError)
