from functools import partial
from functools import wraps
import logging
import time

def retry_on_error(nretries=1, retry_interval=2):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
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

def retry_wrapper(f, fargs=None, fkwargs=None, nretries=1, retry_interval=2):
    '''Retry on error with parameters of how many times (nretries)
    and interval in seconds (retry_interval).
    If the function to be decorated is an instance method
    and the values come from a configuration,
    then this decorator can retrieve these two parameters
    from instance attributes with the same name.
    Otherwise, use the default values or pass new values to the decorator.
    '''
    time2sleep = 1
    logger = logging.getLogger()
    for i in range(nretries + 1):
        try:
            return f(*fargs, **fkwargs)
        except Exception as e:
            if i == nretries:
                logger.error("Error Function {:s} giving up with {:s} after {:d} retry".format(f.__name__, e, i))
                raise e
            logger.warning("Function {:s} failed with {:s} on try {:d}/{:d}. Sleeping {:d} seconds".format(f.__name__, e, i, nretries, time2sleep))
            time.sleep(time2sleep)
            time2sleep *= retry_interval
