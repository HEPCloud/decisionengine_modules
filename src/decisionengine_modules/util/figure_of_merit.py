"""
Calculate figure of merit
"""

import sys

_INFINITY = sys.float_info.max


def figure_of_merit(performance,
                    running,
                    allowed,
                    logger,
                    idle=None,
                    max_idle=None):

    logger = logger.bind(module=__name__.split(".")[-1])

    try:
        if running >= allowed or allowed == 0:
            return _INFINITY
        if idle is not None and max_idle is not None:
            if idle >= max_idle:
                return _INFINITY
        return performance * float(running + 1) / allowed
    except TypeError:
        logger.exception("TypeError in figure_of_merit")
    except Exception:
        logger.exception("Unexpected error in figure_of_merit")
        raise
