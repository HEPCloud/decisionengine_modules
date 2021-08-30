from functools import partial
from functools import wraps
import structlog
import time

from decisionengine.framework.modules.logging_configDict import CHANNELLOGGERNAME

def retry_on_error(nretries=1, retry_interval=2, backoff=True):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return retry_wrapper(partial(f, *args, **kwargs), nretries, retry_interval, backoff)
        return wrapper
    return decorator

def retry_wrapper(f, nretries=1, retry_interval=2, backoff=True):
    '''Retry on error with parameters of how many times (nretries)
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
    for i in range(nretries + 1):
        try:
            return f()
        except Exception as e:
            fname = 'Unknown'
            if hasattr(f, '__name__'):
                fname = f.__name__
            elif hasattr(f, 'func'):
                fname = f.func.__name__
            if i == nretries:
                logger.exception("Error Function {} giving up with {} after {} retries".format(fname, e, i))
                raise e
            logger.warning("Function {} failed with {} on try {}/{}. Sleeping {:d} seconds".format(fname, e, i, nretries, time2sleep))
            time.sleep(time2sleep)
            if backoff:
                time2sleep *= retry_interval
