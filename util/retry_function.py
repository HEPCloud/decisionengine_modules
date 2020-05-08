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

            time2sleep = 1
            logger = logging.getLogger()
            for i in range(nretries + 1):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if i == nretries:
                        logger.error("Error Function {:s} giving up with {:s} after {:d} retry".format(f.__name__, e, i))
                        raise e
                    logger.warning("Function {:s} failed with {:s} on try {:d}/{:d}. Sleeping {:d} seconds".format(f.__name__, e, i, nretries, time2sleep))
                    time.sleep(time2sleep)
                    time2sleep *= retry_interval

        return wrapper
    return decorator
