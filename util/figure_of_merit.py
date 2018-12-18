"""
Calculate figure of merit
"""

import sys

_INFINITY = sys.float_info.max

def figure_of_merit(performance,
                    running,
                    allowed):
    if running >= allowed:
        return _INFINITY
    return performance*float(running+1)/allowed


