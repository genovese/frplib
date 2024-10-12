from __future__ import annotations

import pytest

from hypothesis             import given
from hypothesis.strategies  import integers, decimals, tuples, lists, one_of, dictionaries

from frplib.exceptions   import ConstructionError
from frplib.expectations import E
from frplib.frps         import FRP, frp, conditional_frp, PureExpression, MixtureExpression, evolve
from frplib.kinds        import Kind, kind, conditional_kind, constant, either, uniform, weighted_as
from frplib.quantity     import as_quantity
from frplib.statistics   import __, Proj
from frplib.utils        import dim, codim, typeof, clone, const
from frplib.vec_tuples   import as_vec_tuple, join

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
    u = conditional_frp({0: frp(either(0, 1)), 1: frp(uniform(1, 2, 3)), 2: frp(uniform(4, 5))})
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

    f2 = conditional_frp(k1)
    f12 = f1 * f2
    assert f12(0).value == join(f1(0).value, f2.target(0).value)
    assert f12(1).value == join(f1(1).value, f2.target(1).value)
    assert f12(2).value == join(f1(2).value, f2.target(2).value)

    f1_3 = f1 ** 3
    assert f1_3(0).dim == 4
    assert f1_3(1).dim == 4
    assert f1_3(2).dim == 4

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

    with pytest.raises(ConstructionError):
        conditional_frp(__)

    with pytest.raises(ConstructionError):
        conditional_frp(2)

    with pytest.raises(ConstructionError):
        conditional_frp([])


def test_auto_clone():
    "Testing caching and auto cloning in conditional FRPs"
    fu = conditional_frp({0: frp(either(0, 1)), 1: frp(uniform(3, 4, 5))})
    fc = conditional_frp({0: frp(either(0, 1)), 1: frp(uniform(3, 4, 5))}, auto_clone=True)

    v0 = fu(0).value
    assert all(fu(0).value == v0 for _ in range(32))

    fc0 = fc(0)
    vc0 = fc0.value
    vck = kind(fc0)
    assert not all(fc(0).value == vc0 for _ in range(128))
    assert all(Kind.equal(vck, kind(fc(0))) for _ in range(16))

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
    assert u1_v[0] == U.value[0] ** 2 + 10

    X = frp(uniform(1, 2, 3))
    Y = frp(uniform(1, 2, 3))
    assert X.is_fresh and Y.is_fresh
    XY = X * Y
    assert XY.is_fresh
    
    xy_val = join(X.value, Y.value)
    assert not XY.is_fresh
    assert XY.value == xy_val

    ck = conditional_kind({0: uniform(1, 2, 3), 1: either(4, 5), 2: constant(10)})
    cf = conditional_frp(ck)
    R = frp(uniform(0, 1, 2))
    assert R.is_fresh
    assert cf(0).is_fresh and cf(1).is_fresh and cf(2).is_fresh
    RC = R >> cf
    assert RC.is_fresh
    rc_val = cf(R.value).value
    assert not RC.is_fresh
    assert RC.value == rc_val

def test_expressions():
    u = PureExpression(frp(uniform(1, 2, 3)))
    cf = conditional_frp({1: frp(either(2,3)), 2: frp(either(4, 5)), 3: frp(either(5, 6))})
    v = MixtureExpression(u, cf)
    r = uniform( (1, 2), (1, 3), (2, 4), (2, 5), (3, 5), (3, 6) )

    assert Kind.equal(kind(u), uniform(1, 2, 3))
    assert Kind.equal(kind(frp(v)), r)

def test_evolve():
    small = as_quantity(1e-18)
    half = as_quantity(1/2)

    @conditional_kind(codim=1)
    def stepk(current):
        return uniform(-1, 1) ^ (__ + current)

    step = conditional_frp(stepk, auto_clone=True)
    init = frp(constant(0))

    # Weak test, just ensuring that things run reasonably well
    ev = evolve(init, step, 50, transform=FRP.activate)
    assert -50 <= ev.value[0] <= 50

def kind_gen(d, s):
    weights = decimals(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False)
    values = lists(decimals(min_value=-5000, max_value=5000, allow_nan=False, allow_infinity=False), min_size=d, max_size=d).map(as_vec_tuple)   # type: ignore
    kinds = dictionaries(values, weights, min_size=s, max_size=s).map(weighted_as)
    return kinds

@given(kind_gen(2, 5))
def test_transform_gen(k):
    X = frp(k)
    assert X.value in k.weights
    assert (Proj[1](X)).value == X.value[:1]

    Y = frp(k)
    assert (X * Y).value == join(X.value, Y.value)

    cF = conditional_frp({0: X, 1: Y})
    U = frp(either(0, 1))
    Z = U >> cF
    if U.value == 0:
        assert Z.value == join(0, X.value)
    else:
        assert Z.value == join(1, Y.value)

    assert E(X) == E(k)
