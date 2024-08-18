from __future__ import annotations

import pytest

from frplib.frps       import frp, conditional_frp
from frplib.kinds      import Kind, kind, constant, either, uniform
from frplib.statistics import __, Proj
from frplib.utils      import dim, const

def test_empty_conditional():
    X = frp(uniform(1, 2, ..., 8))
    a = X.value
    Y = X | (__ < a)
    Z = X | (__ <= a)

    assert dim(Y) == 0
    assert Z.value == X.value

def test_frp_transform():
    X = frp(uniform(0, 1, ..., 7))
    assert Kind.equal(kind(X ^ (__ + 1)), uniform(1, 2, ..., 8))
    assert Kind.equal(kind(X ^ const(0)), constant(0))
    assert Kind.equal(kind(X * X ^ Proj[1]), kind(X))
    assert Kind.equal(kind(X * X ^ Proj[2]), kind(X))


#
# Tests of Conditional FRPs and related operations
#

def test_conditional_frps():
    u = conditional_frp({0: frp(either(0, 1)), 1: frp(uniform(1, 2, 3)), 2: frp(uniform(4, 5))})  # type: ignore
    v = frp(uniform(0, 1, 2))

    assert Kind.equal(kind(v >> u ^ Proj[2]), kind(u // v))  # tests fix of Bug 10
