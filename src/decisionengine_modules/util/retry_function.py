import time

from functools import partial, wraps


def retry_on_error(nretries=1, retry_interval=2, backoff=True):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return retry_wrapper(partial(f, *args, **kwargs), nretries, retry_interval, backoff)

        return wrapper

    return decorator


def retry_wrapper(f, nretries=1, retry_interval=2, backoff=True, logger=None):
    """Retry on error with parameters of how many times (nretries)
    and interval in seconds (retry_interval).
    If the function to be decorated is an instance method
    and the values come from a configuration,
    then this decorator can retrieve these two parameters
    from instance attributes with the same name.
    Otherwise, use the default values or pass new values to the decorator.
    """
    time2sleep = retry_interval
    for i in range(nretries + 1):
        try:
            return f()
        except Exception as e:
            fname = "Unknown"
            if hasattr(f, "__name__"):
                fname = f.__name__
            elif hasattr(f, "func"):
                fname = f.func.__name__
            if i == nretries:
                if logger is not None:
                    logger.exception(f"Error Function {fname} giving up with {e} after {i} retries")
                raise e
            if logger is not None:
                logger.warning(
                    f"Function {fname} failed with {e} on try {i}/{nretries}. Sleeping {time2sleep:d} seconds"
                )
            time.sleep(time2sleep)
            if backoff:
                time2sleep *= retry_interval
