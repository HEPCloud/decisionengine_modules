# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Calculate figure of merit
"""

import sys

from decisionengine.framework.util.metrics import Gauge

_INFINITY = sys.float_info.max

FIGURE_OF_MERIT_CALCULATION = Gauge(
    "figure_of_merit_calculation",
    "Figure of Merit Calculation",
    ["performance", "running", "max_allowed", "idle", "max_idle"],
)


def figure_of_merit(performance, running, max_allowed, idle=None, max_idle=None, logger=None):
    try:
        if running >= max_allowed or max_allowed == 0:
            return _INFINITY
        if idle is not None and max_idle is not None and idle >= max_idle:
            return _INFINITY
        fom_value = performance * float(running + 1) / max_allowed
        return fom_value
    except TypeError:
        if logger is not None:
            logger.exception("TypeError in figure_of_merit")
    except Exception:
        if logger is not None:
            logger.exception("Unexpected error in figure_of_merit")
        raise
