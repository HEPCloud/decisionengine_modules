# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from functools import partial

import pytest

import decisionengine_modules.util.retry_function as retry_function


class Dummy:
    def __init__(self):
        self.max_retries = 2
        self.retry_interval = 2

    def _sum(self, foo, input2):
        return foo + input2 + self.max_retries + self.retry_interval

    def _func_success(self, foo, input2):
        return self._sum(foo, input2)

    def func_success(self, foo, input2):
        return retry_function.retry_wrapper(
            partial(self._func_success, foo, input2), self.max_retries, self.retry_interval
        )

    def _func_failure(self, foo, input2):
        raise ValueError(self._sum(foo, input2))

    def func_failure(self, foo, input2):
        return retry_function.retry_wrapper(
            partial(self._func_failure, foo, input2), self.max_retries, self.retry_interval
        )


def test_all():
    d = Dummy()
    assert d.func_success(2, input2=4) == 10

    with pytest.raises(ValueError) as e:
        d.func_failure(2, input2=4)
    assert e.value.args[0] == 10
