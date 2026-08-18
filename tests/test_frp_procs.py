"""Tests of FRP procedures that use the @frp decorator on nullary generator function defs."""

# pylint: disable=invalid-name, missing-function-docstring, disallowed-name

from __future__ import annotations

import pytest

from frplib.exceptions import ConstructionError, FrpError
from frplib.frps       import FRP, frp, conditional_frp
from frplib.kinds      import Kind, binary, constant, choice, given, kind, weighted_as, uniform
from frplib.statistics import __, Proj, Sum
from frplib.vec_tuples import vec_tuple

k1 = binary()
k2 = uniform(1, 2, ..., 8)
k3 = weighted_as(1, 10, 100, weights=[2, 5, 3])
k4 = uniform(1, 2, ..., 24)
k5 = weighted_as(-8, 16, 64, 128, weights=[4, 1, 2, 3])
k6 = constant(99)


def test_frp_procs_trans():
    @frp
    def A():
        x = yield frp(k4)
        return (x - 12) ** 2

    @frp
    def B():
        x = yield frp(k1 * k2 * k5)
        return sum(x)

    @frp
    def C():
        x = yield frp(k2 * k3 * k6)
        return x[1]

    assert FRP.sample(1024, A).values_seen() == set(vec_tuple(j * j) for j in range(13))
    assert FRP.sample(1280, B).values_seen() == FRP.sample(1280, Sum(k1 * k2 * k5)).values_seen()
    assert FRP.sample(1024, C).values_seen() == FRP.sample(1024, k3).values_seen()

    assert Kind.equal(kind(A), k4 ^ ((__ - 12) ** 2))
    assert Kind.equal(kind(B), (k1 * k2 * k5) ^ Sum)
    assert Kind.equal(kind(C), (k2 * k3 * k6) ^ Proj[2])
    assert Kind.equal(kind(C), k3)

def test_frp_procs_ijoins():
    @frp
    def Ijoin1():
        x = yield k1
        y = yield frp(k2)
        return (x, y)

    @frp
    def Ijoin2():
        x = yield k1
        y = yield k2
        z = yield k3
        return (x, y, z)

    @frp
    def Ijoin3():
        x = yield frp(choice(1, 2))
        y = yield frp(choice(1, 2))
        z = yield frp(choice(1, 2))
        return (x, y, z)

    assert Kind.equal(kind(Ijoin1), k1 * k2)
    assert Kind.equal(kind(Ijoin2), k1 * k2 * k3)
    assert Kind.equal(kind(Ijoin3), choice(1, 2) ** 3)

    vals12 = set(vec_tuple(i, j) for i in [0, 1] for j in range(1, 9))
    assert FRP.sample(1024, Ijoin1).values_seen() == vals12

    vals123 = set(vec_tuple(i, j, k) for i in [0, 1] for j in range(1, 9) for k in [1, 10, 100])
    assert FRP.sample(1024, Ijoin2).values_seen() == vals123

    vals_bin = set(vec_tuple(i, j, k) for i in [1, 2] for j in [1, 2] for k in [1, 2])
    assert FRP.sample(256, Ijoin3).values_seen() == vals_bin

def test_frp_procs_gjoins():
    cf = conditional_frp({
        0: frp(uniform(1, 2, 3, 4)),
        1: frp(choice(-50, 5))
    })

    @frp
    def A():
        x = yield binary()
        y = yield cf.target(x)   # ATTN: replce with cf(x) after target/joined switch
        return (x, y)

    @frp
    def B():
        x = yield binary()
        y = yield cf.target(x)   # ATTN: replce with cf(x) after target/joined switch
        return y

    assert Kind.equal(kind(A), binary() >> kind(cf))
    assert Kind.equal(kind(B), kind(cf) // binary())

    valsA = set(vec_tuple(0, i) for i in [1, 2, 3, 4])
    valsA = valsA.union(vec_tuple(1, i) for i in [-50, 5])
    assert FRP.sample(1024, A).values_seen() == valsA


def test_frp_procs_obs():
    @frp
    def A():
        x = yield frp(k5)
        yield given(x > 20)
        return (x - 12) ** 2

    @frp
    def A2():
        x = yield k4
        yield given(x % 2 == 0)
        return x

    assert FRP.sample(128, A).values_seen() == set([vec_tuple(2704), vec_tuple(13456)])
    assert Kind.equal(kind(A), (k5 | (__ > 20)) ^ ((__ - 12) ** 2))
    assert FRP.sample(128, A2).values_seen() == set(vec_tuple(2 * k) for k in range(1, 13))
    assert Kind.equal(kind(A2), k4 | (__ % 2 == 0))

    for _ in range(32):
        B0 = frp(k5)
        C0 = frp(k4)

        @frp
        def B(src=B0):
            x = yield src
            yield given(x > 0)
            return x

        @frp
        def C(src=C0):
            x = yield src
            yield given(x % 2 == 0)
            return x

        if B0.value[0] > 0:
            assert B0.value == B.value

        if C0.value[0] % 2 == 0:
            assert C0.value == C.value

def test_frp_proc_errors():
    with pytest.raises(ConstructionError, match=r'no required positional arguments'):
        @frp                    # type: ignore
        def foo(_u):
            x = yield k1
            return x + 1

    @frp
    def arg_ok(u=10):    # Args with defaults are ok
        x = yield k6
        return x + u

    assert arg_ok.value == 109

    with pytest.raises(ConstructionError, match=r'should be a generator function'):
        @frp
        def non_gen():
            return 17

    @frp
    def bar():
        x = yield 17
        return x + 1

    with pytest.raises(FrpError, match=r'should be an FRP'):
        bar.value          # pylint: disable=pointless-statement
