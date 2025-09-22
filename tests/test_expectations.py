from __future__ import annotations

import math
import pytest

from decimal import Decimal
from typing  import cast, Union

from frplib.exceptions   import MismatchedDomain
from frplib.expectations import E, Var
from frplib.frps         import conditional_frp, frp, average_conditional_entropy, mutual_information
from frplib.kinds        import conditional_kind, constant, either, uniform, weighted_as
from frplib.quantity     import as_quantity
from frplib.statistics   import Statistic
from frplib.symbolic     import simplify, symbol

def test_expectation():
    assert uniform(1, 2, 3).expectation == Decimal(2)
    assert frp(uniform(1, 2, 3)).expectation == Decimal(2)
    assert constant(10).expectation == Decimal(10)
    assert frp(constant(10)).expectation == Decimal(10)

    assert uniform(1, 2, 3, 4).entropy == Decimal(2)
    assert constant(10).entropy == Decimal(0)

    ck = conditional_kind({0: uniform(1, 2, 3, 4), 1: weighted_as(10, 20, 50, 100, weights=[4, 2, 1, 3])})
    cf = frp(ck)

    assert isinstance(ck.expectation, Statistic)
    assert isinstance(cf.expectation, Statistic)

    assert ck.expectation(0) == Decimal('2.5')
    assert cf.expectation(0) == Decimal('2.5')
    assert ck.expectation(1) == Decimal('43.0')
    assert cf.expectation(1) == Decimal('43.0')

    assert ck.conditional_entropy(0) == Decimal(2)
    assert ck.conditional_entropy(1)[0] == pytest.approx(Decimal('1.846439344671015493434197746'))

    assert average_conditional_entropy(either(0, 1), ck) == pytest.approx(Decimal('1.923219672335507746717098873'))
    assert mutual_information(either(0, 1), ck) == pytest.approx(Decimal('1.0'))  # ATTN: Check this

def test_symbolic_E():
    p = symbol('p')
    k0 = weighted_as(-1, 0, 1, weights=[1, p, p**2])
    assert E(k0).raw == simplify((p**2 - 1) / (1 + p + p**2))  # tests fix of Bug 20

def test_variance():
    assert math.isclose(Var(uniform(-1, 0, 1)).raw, cast(Union[int, Decimal], as_quantity('2/3')))

    k1 = conditional_kind({0: either(0, 1), 1: either(0, 2), 2: either(0, 3)})
    f = Var(k1)

    assert f(0).raw == as_quantity('1/4')
    assert f(1).raw == as_quantity('1')
    assert f(2).raw == as_quantity('9/4')

    with pytest.raises(MismatchedDomain):
        f(3)

    x1 = conditional_frp(k1)
    g = Var(x1)

    assert g(0).raw == as_quantity('1/4')
    assert g(1).raw == as_quantity('1')
    assert g(2).raw == as_quantity('9/4')

    with pytest.raises(MismatchedDomain):
        g(3)
