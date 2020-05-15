from retry_function import *
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


success_string="INFO:root:Hello World"

failure_string='''WARNING:root:Function _func_failure failed with A very specific bad thing happened. on try 0/2. Sleeping 1 seconds
WARNING:root:Function _func_failure failed with A very specific bad thing happened. on try 1/2. Sleeping 2 seconds
ERROR:root:Error Function _func_failure giving up with A very specific bad thing happened. after 2 retries'''

class Dummy:

    def __init__(self, name="Dummy"):
        self.name = name
        self.nretries = 2
        self.retry_interval = 2

    def _func_success(self, foo, text="World"):
        logger = logging.getLogger()
        logger.info(foo + " " + text)

    def func_success(self, foo, text="World"):
        return retry_wrapper( partial(self._func_success, *(foo,), **{"text": "World"}), self.nretries, self.retry_interval)

    def _func_failure(self, foo, text="World"):
        raise ValueError('A very specific bad thing happened.')

    def func_failure(self, foo, text="World"):
        return retry_wrapper(partial(self._func_failure, *(foo,), **{"text": "World"}), self.nretries, self.retry_interval)


log_stream = StringIO()
logging.basicConfig(stream=log_stream, level=logging.INFO)
mystr_handler = logging.StreamHandler()

def test_all():
    d = Dummy()
    d.func_success("Hello")
    assert success_string == log_stream.getvalue().rstrip()

    log_stream.truncate(0)

# testing a failure handling
    try:
        d.func_failure("Hi")
    except:
        pass
    finally:
        assert failure_string == log_stream.getvalue().rstrip()
