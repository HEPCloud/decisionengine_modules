from functools import partial
from functools import wraps
import structlog
import time

from decisionengine.framework.modules.logging_configDict import CHANNELLOGGERNAME

def retry_on_error(max_retries=1, retry_interval=2, backoff=True):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return retry_wrapper(partial(f, *args, **kwargs), max_retries, retry_interval, backoff)
        return wrapper
    return decorator


def retry_wrapper(f, max_retries=1, retry_interval=2, backoff=True, logger=None):
    '''Retry on error with parameters of how many times (max_retries)
    and interval in seconds (retry_interval).
    If the function to be decorated is an instance method
    and the values come from a configuration,
    then this decorator can retrieve these two parameters
    from instance attributes with the same name.
    Otherwise, use the default values or pass new values to the decorator.
    '''
    time2sleep = retry_interval
    logger = structlog.getLogger(CHANNELLOGGERNAME)
    logger = logger.bind(module=__name__.split(".")[-1], channel="")
    for i in range(max_retries + 1):
        try:
            return f()
        except Exception as e:
            fname = 'Unknown'
            if hasattr(f, '__name__'):
                fname = f.__name__
            elif hasattr(f, 'func'):
                fname = f.func.__name__
            if i == max_retries:
                if logger is not None:
                    logger.exception(f"Error Function {fname} giving up with {e} after {i} retries")
                raise e
            if logger is not None:
                logger.warning(
                    f"Function {fname} failed with {e} on try {i}/{max_retries}. Sleeping {time2sleep:d} seconds"
                )
            time.sleep(time2sleep)
            if backoff:
                time2sleep *= retry_interval
