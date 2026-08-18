"""Tests of basic FRP infrastructure."""

# pylint: disable=invalid-name, missing-function-docstring, disallowed-name, pointless-statement

from __future__ import annotations

import pytest

from hypothesis             import given
from hypothesis.strategies  import decimals, lists, dictionaries

from frplib.exceptions   import ConstructionError, FrpError
from frplib.expectations import E
from frplib.frps         import FRP, frp, conditional_frp, PureExpression, JoinExpression, evolve
from frplib.kinds        import Kind, kind, conditional_kind, choice, constant, uniform, weighted_as
from frplib.quantity     import as_quantity
from frplib.statistics   import __, Proj
from frplib.utils        import dim, codim, typeof, clone, const
from frplib.vec_tuples   import VecTuple, as_vec_tuple


def test_observations_nonfresh_or_empty():
    X = frp(uniform(1, 2, ..., 8))
    a = X.value
    if a > 1:  # If a == 1, __ < a is impossible
        Y = X | (__ < a)
    Z = X | (__ <= a)

    if a > 1:  # If a == 1, Y will be the empty FRP
        assert Y.value < a
    assert Z.value == X.value

    U = frp(uniform(1, 2, ..., 10))
    with pytest.raises(FrpError):
        U | (__ == 11)

def test_frp_transform():
    X = frp(uniform(0, 1, ..., 7))
    assert Kind.equal(kind(X ^ (__ + 1)), uniform(1, 2, ..., 8))
    assert Kind.equal(kind(X ^ const(0)), constant(0))
    assert Kind.equal(kind(X * X ^ Proj[1]), kind(X))
    assert Kind.equal(kind(X * X ^ Proj[2]), kind(X))

    assert E(X).raw == as_quantity('7/2')

    Y = X ^ (__ + 1)
    assert Y.value == X.value + 1
    Y = X ^ const(0)
    assert Y.value == 0
    Y = X * X ^ Proj[1]
    assert Y.value == X.value
    Y = X * X ^ Proj[2]
    assert Y.value == X.value


#
# Tests of Conditional FRPs and related operations
#

def test_conditional_frps():
    u = conditional_frp({0: frp(choice(0, 1)), 1: frp(uniform(1, 2, 3)), 2: frp(uniform(4, 5))})
    v = frp(uniform(0, 1, 2))

    assert Kind.equal(kind(v >> u ^ Proj[2]), kind(u // v))  # tests fix of Bug 10

    k1 = conditional_kind({0: choice(0, 1), 1: choice(0, 2), 2: choice(0, 3)})
    f1 = conditional_frp(k1)

    assert typeof(f1) == '1 -> 2'
    assert typeof(f1) == typeof(clone(f1))
    for j in range(3):
        assert Kind.equal(kind(f1(j)), kind(clone(f1)(j)))
        assert Kind.equal(kind(f1.joined(j)), kind(clone(f1).joined(j)))

    z = frp(uniform(0, 1, 2))
    zf = z >> f1
    assert zf.value == f1.joined(z.value).value
    for _ in range(5):
        z2 = clone(z)
        f2 = clone(f1)
        z2f = z2 >> f2
        assert z2f.value == f2.joined(z2.value).value

    assert dim(f1 // z) == 1
    # print(zf, dim(zf))
    assert (f1 // z).value == zf[2].value

    f2 = conditional_frp(k1)
    f12 = f1 * f2
    assert f12.target(0).value == VecTuple.join(f1.target(0).value, f2.target(0).value)  # type: ignore[type-var]
    assert f12.target(1).value == VecTuple.join(f1.target(1).value, f2.target(1).value)  # type: ignore[type-var]
    assert f12.target(2).value == VecTuple.join(f1.target(2).value, f2.target(2).value)  # type: ignore[type-var]
    assert f12.joined(0).value == VecTuple.join(f1.joined(0).value, f2.target(0).value)  # type: ignore[type-var]
    assert f12.joined(1).value == VecTuple.join(f1.joined(1).value, f2.target(1).value)  # type: ignore[type-var]
    assert f12.joined(2).value == VecTuple.join(f1.joined(2).value, f2.target(2).value)  # type: ignore[type-var]

    f1_3 = f1 ** 3
    assert f1_3(0).dim == 3
    assert f1_3(1).dim == 3
    assert f1_3(2).dim == 3
    assert f1_3.target(0).dim == 3
    assert f1_3.target(1).dim == 3
    assert f1_3.target(2).dim == 3
    assert f1_3.joined(0).dim == 4
    assert f1_3.joined(1).dim == 4
    assert f1_3.joined(2).dim == 4

    k2 = conditional_kind({(0, 0): choice(10, 20),
                           (0, 1): choice(30, 40),
                           (1, 0): choice(50, 60),
                           (1, 2): choice(70, 80),
                           (2, 0): choice(90, 95),
                           (2, 3): choice(96, 99)})
    f2 = conditional_frp(k2)

    assert codim(f2) == 2
    assert dim(f2) == 3
    assert typeof(f2) == '2 -> 3'

    zf_check = z >> f1
    assert zf.value == zf_check.value

    zz = z >> f1 >> f2
    assert dim(zz) == 3
    assert zz.value == f2.joined(zf.value).value

    assert Kind.equal(kind(zz), uniform(0, 1, 2) >> k1 >> k2)

    with pytest.raises(ConstructionError):
        conditional_frp(__)

    with pytest.raises(ConstructionError):
        conditional_frp(2)    # type: ignore

    with pytest.raises(ConstructionError):
        conditional_frp([])   # type: ignore


def test_auto_clone():
    "Testing caching and auto cloning in conditional FRPs"
    fu = conditional_frp({0: frp(choice(0, 1)), 1: frp(uniform(3, 4, 5))})
    fc = conditional_frp({0: frp(choice(0, 1)), 1: frp(uniform(3, 4, 5))}, auto_clone=True)

    v0 = fu.joined(0).value
    assert all(fu.joined(0).value == v0 for _ in range(32))

    fc0 = fc.joined(0)
    vc0 = fc0.value
    vck = kind(fc0)
    assert not all(fc.joined(0).value == vc0 for _ in range(128))
    assert all(Kind.equal(vck, kind(fc.joined(0))) for _ in range(16))

def test_ops():
    k = uniform(1, 2, ..., 6) ** 2
    X = frp(k)
    v = X.value
    Xc = Proj[2] @ X | (Proj[1] == v[0])
    assert Xc.value == as_vec_tuple(v[1])

    with pytest.raises(TypeError):
        X >> 2

    with pytest.raises(TypeError):
        X >> X

    with pytest.raises(TypeError):
        X >> __

    with pytest.raises(TypeError):
        X * k

def test_freshness():
    "Tests that values and freshness of FRPs propagate properly."
    U = frp(uniform(1, 2, ..., 5))
    assert U.is_fresh
    U1 = U ^ (__ ** 2 + 10)
    assert U1.is_fresh
    u1_v = U1.value
    assert not U1.is_fresh and not U.is_fresh
    assert u1_v[0] == U.value[0] ** 2 + 10     # type: ignore  # U1's freshness state changed

    X = frp(uniform(1, 2, 3))
    Y = frp(uniform(1, 2, 3))
    assert X.is_fresh and Y.is_fresh
    XY = X * Y
    assert XY.is_fresh

    xy_val = VecTuple.join(X.value, Y.value)
    assert not XY.is_fresh
    assert XY.value == xy_val

    ck = conditional_kind({0: uniform(1, 2, 3), 1: choice(4, 5), 2: constant(10)})
    cf = conditional_frp(ck)
    R = frp(uniform(0, 1, 2))
    assert R.is_fresh
    assert cf.joined(0).is_fresh and cf.joined(1).is_fresh and cf.joined(2).is_fresh
    RC = R >> cf
    assert RC.is_fresh
    rc_val = cf.joined(R.value).value
    assert not RC.is_fresh
    assert RC.value == rc_val

def test_expressions():
    u = PureExpression(frp(uniform(1, 2, 3)))
    cf = conditional_frp({1: frp(choice(2, 3)), 2: frp(choice(4, 5)), 3: frp(choice(5, 6))})
    v = JoinExpression(u, cf)
    r = uniform( (1, 2), (1, 3), (2, 4), (2, 5), (3, 5), (3, 6) )

    assert Kind.equal(kind(u), uniform(1, 2, 3))
    assert Kind.equal(kind(frp(v)), r)

def test_evolve():
    # small = as_quantity(1e-18)
    # half = as_quantity(1 / 2)

    @conditional_kind(codim=1)
    def stepk(current):
        return uniform(-1, 1) ^ (__ + current)

    step = conditional_frp(stepk, auto_clone=True)
    init = frp(constant(0))

    # Weak test, just ensuring that things run reasonably well
    ev = evolve(init, step, 50, transform=FRP.activate)
    assert -50 <= ev.value[0] <= 50

def test_entropy():  # Test Issue 55
    assert frp(constant(1)).entropy == pytest.approx(0)
    assert frp(uniform(1, 2)).entropy == pytest.approx(1)
    assert frp(uniform(1, 2, ..., 4)).entropy == pytest.approx(2)
    assert frp(uniform(1, 2, ..., 8)).entropy == pytest.approx(3)
    assert frp(uniform(1, 2, ..., 16)).entropy == pytest.approx(4)
    assert frp(uniform(1, 2, ..., 32)).entropy == pytest.approx(5)

def kind_gen(d, s):
    weights = decimals(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False)
    values = lists(
        decimals(min_value=-5000, max_value=5000, allow_nan=False, allow_infinity=False),
        min_size=d, max_size=d
    ).map(as_vec_tuple)   # type: ignore
    kinds = dictionaries(values, weights, min_size=s, max_size=s).map(weighted_as)
    return kinds

@given(kind_gen(2, 5))
def test_transform_gen(k):
    X = frp(k)
    assert X.value in k.weights
    assert (Proj[1](X)).value == X.value[:1]

    Y = frp(k)
    assert (X * Y).value == VecTuple.join(X.value, Y.value)

    cF = conditional_frp({0: X, 1: Y})
    U = frp(choice(0, 1))
    Z = U >> cF
    if U.value == 0:
        assert Z.value == VecTuple.join(0, X.value)
    else:
        assert Z.value == VecTuple.join(1, Y.value)

    assert E(X) == E(k)
