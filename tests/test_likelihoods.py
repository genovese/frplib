# pylint: disable=too-many-statements, too-many-function-args, line-too-long, invalid-name, missing-function-docstring

from __future__ import annotations

import math
import pytest

from frplib.kinds      import constant, ijoin_log_kernel, ijoin_log_likelihood, uniform
from frplib.statistics import infinity


def test_log_likelihood():
    f = ijoin_log_likelihood(1, 2, 3)
    assert math.isclose(f(uniform(1, 2, 3)), -math.log(3 ** 3))

    g = ijoin_log_likelihood(1, 2, 3, 1, 2, 3, 1, 2, 3)
    assert math.isclose(g(uniform(1, 2, 3)), -math.log(3 ** 9))

    h = ijoin_log_likelihood(1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3)
    assert math.isclose(h(uniform(1, 2, 3)), -math.log(3 ** 12))
    assert math.isclose(h(uniform(1, 2, 3) ** 3), -math.log(3 ** 12))

    assert math.isclose(ijoin_log_likelihood(*([4] * 10))(constant(4)), 0.0)
    assert ijoin_log_likelihood(*([4] * 10))(constant(99)) == -infinity

    v = ijoin_log_kernel(uniform(1, 2, 3))
    assert math.isclose(h(uniform(1, 2, 3)), v(1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3))
