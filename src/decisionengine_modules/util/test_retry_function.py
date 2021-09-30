from functools import partial
import decisionengine_modules.util.retry_function as retry_function

class Dummy:

    def __init__(self, name="Dummy"):
        self.name = name
        self.max_retries = 2
        self.retry_interval = 2

    def _func_success(self, foo, input2=3):
        return foo + input2 + self.max_retries + self.retry_interval

    def func_success(self, foo, input2=3):
        return retry_function.retry_wrapper(
            partial(self._func_success, *(foo,), **{"input2": input2}), self.max_retries, self.retry_interval
        )

    def _func_failure(self, foo, input2=3):
        raise ValueError({"sum": foo + input2 + self.max_retries + self.retry_interval})

    def func_failure(self, foo, input2=3):
        return retry_function.retry_wrapper(
            partial(self._func_failure, *(foo,), **{"input2": input2}), self.max_retries, self.retry_interval
        )


def test_all():
    d = Dummy()
    sum1 = d.func_success(2, input2=4)
    assert sum1 == 10

    sum2 = 0
    try:
        d.func_failure(2, input2=4)
    except ValueError as e:
        sum2 = e.args[0].get('sum')

    assert sum2 == 10
