#!/usr/bin/env python
import importlib
import string
import pprint

"""
Load python object
"""

def load(python_file):
    """
    Load constants from file.

    :type constants_file: :obj:`file`
    :arg constants_file: configuration file as python dict

    :rtype: :obj:`object`

    """

    code = None
    with open(python_file, "r") as f:
        code = "config=" + string.join(f.readlines(), "")
    if code:
        exec(code)

    return config

if __name__ == '__main__':
    config = load('spot_price_config_sample.py')
    print config
