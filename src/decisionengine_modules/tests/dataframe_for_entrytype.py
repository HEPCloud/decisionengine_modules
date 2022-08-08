# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas as pd


def dataframe_for_entrytype(key, data):
    return pd.concat({key: pd.DataFrame(data)})
