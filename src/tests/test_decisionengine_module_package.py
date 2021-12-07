# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Make sure decisionengine_modules is a valid python package
"""


def test_can_import():
    import decisionengine_modules  # noqa: F401

    pass
