# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
    Utils to simplify testing
"""
import datetime  # noqa: F401

import pandas as pd  # noqa: F401

# These imports needed for the `eval` blocks
from classad import classad  # noqa: F401


def input_from_file(fname):
    with open(fname) as fd:
        return eval(fd.read())


def raw_input_from_file(fname):
    with open(fname) as fd:
        return fd.read()


def compare_dfs(df1, df2):
    """
    for some reason df.equals does not work here
    but if I compare cell by cell it works
    :type df1: :class:`pd.DataFrame`
    :arg df1: data frame instance
    :type df2: :class:`pd.DataFrame`
    :arg df2: data frame instance
    :rtype: :obj:`bool` - True if equal

    """
    if df1.shape[0] != df2.shape[0]:
        return False
    if df1.shape[1] != df2.shape[1]:
        return False
    rc = True
    for i in range(df1.shape[0]):
        for j in range(df1.shape[1]):
            if df1.iloc[i, j] != df2.iloc[i, j]:
                rc = False
                break
    return rc
