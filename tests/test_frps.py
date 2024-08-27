from __future__ import annotations

import pytest

from frplib.frps       import frp, conditional_frp
from frplib.kinds      import Kind, kind, conditional_kind, constant, either, uniform
from frplib.statistics import __, Proj
from frplib.utils      import dim, codim, typeof, clone, const

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

    k1 = conditional_kind({0: either(0, 1), 1: either(0, 2), 2: either(0, 3)})
    f1 = conditional_frp(k1)   # type: ignore

    assert typeof(f1) == '1 -> 2'
    assert typeof(f1) == typeof(clone(f1))
    for j in range(3):
        assert Kind.equal(kind(f1(j)), kind(clone(f1)(j)))

    z = frp(uniform(0, 1, 2))
    zf = z >> f1
    assert zf.value == f1(z.value).value
    for _ in range(5):
        z2 = clone(z)
        f2 = clone(f1)
        z2f = z2 >> f2
        assert z2f.value == f2(z2.value).value

    assert dim(f1 // z) == 1
    print(zf, dim(zf))
    assert (f1 // z).value == zf[2].value

    k2 = conditional_kind({(0, 0): either(10, 20),
                           (0, 1): either(30, 40),
                           (1, 0): either(50, 60),
                           (1, 2): either(70, 80),
                           (2, 0): either(90, 95),
                           (2, 3): either(96, 99)})
    f2 = conditional_frp(k2)

    assert codim(f2) == 2
    assert dim(f2) == 3
    assert typeof(f2) == '2 -> 3'

    zf_check = z >> f1
    assert zf.value == zf_check.value

    zz = z >> f1 >> f2
    assert dim(zz) == 3
    assert zz.value == f2(zf.value).value

    assert Kind.equal(kind(zz), uniform(0, 1, 2) >> k1 >> k2)

