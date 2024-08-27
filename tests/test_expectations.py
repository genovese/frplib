from __future__ import annotations

import math
import pytest

from frplib.exceptions   import MismatchedDomain
from frplib.expectations import E, Var
from frplib.frps         import conditional_frp
from frplib.kinds        import conditional_kind, either, uniform, weighted_as
from frplib.quantity     import as_quantity
from frplib.symbolic     import simplify, symbol

def test_symbolic_E():
    p = symbol('p')
    k0 = weighted_as(-1, 0, 1, weights=[1, p, p**2])
    assert E(k0).raw == simplify((p**2 - 1) / (1 + p + p**2))  # tests fix of Bug 20

def test_variance():
    assert math.isclose(Var(uniform(-1, 0, 1)).raw, as_quantity('2/3'))

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
