from functools import wraps
import logging
import time

def retry_on_error(nretries=1, retry_interval=2):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            time2sleep = 0
            nretries       = self.nretries
            retry_interval = self.retry_interval
            logger = logging.getLogger()
            for i in range(nretries + 1):
                try:
                    if i != 0:
                        if time2sleep == 0:
                            time2sleep = 1
                        time2sleep *= retry_interval
                    time.sleep(time2sleep)
                    return f(self, *args, **kwargs)
                except Exception as e:
                    logger.warning("Error Function {0:s} failed with {1:s} on try {2:d}/{3:d}".format(f.__name__, e, i, nretries))
                    if i == nretries:
                        logger.error("Error Function {0:s} failed with {1:s} after {2:d} retry".format(f.__name__, e, i))
                        raise e

        return wrapper
    return decorator
