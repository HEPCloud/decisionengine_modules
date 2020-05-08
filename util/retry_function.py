from functools import wraps
import logging
import time

def retry_on_error(nretries=1, retry_interval=2):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            localself = args[0]
            if hasattr(localself, 'nretries'):
                nretries = localself.nretries
            if hasattr(localself, 'retry_interval'):
                retry_interval = localself.retry_interval

            time2sleep = 0
            logger = logging.getLogger()
            for i in range(nretries + 1):
                try:
                    if i != 0:
                        if time2sleep == 0:
                            time2sleep = 1
                        time2sleep *= retry_interval
                    time.sleep(time2sleep)
                    f(*args, **kwargs)
                except Exception as e:
                    logger.warning("Error Function {:s} failed with {:s} on try {:d}/{:d}".format(f.__name__, e, i, nretries))
                    if i == nretries:
                        logger.error("Error Function {:s} failed with {:s} after {:d} retry".format(f.__name__, e, i))
                        raise e

        return wrapper
    return decorator
