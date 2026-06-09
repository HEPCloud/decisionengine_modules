# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Utils to simplify testing
"""
import datetime  # noqa: F401

# These imports needed for the `eval` blocks
try:
    import classad as classad  # noqa: F401  # pylint: disable=import-error
except ImportError:
    import classad2 as classad  # noqa: F401  # pylint: disable=import-error


def input_from_file(fname):
    with open(fname) as fd:
        return eval(fd.read())
