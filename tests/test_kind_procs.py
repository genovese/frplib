"""Tests of Kind procedures that use the @kind decorator on nullary function defs."""

# pylint: disable=invalid-name, missing-function-docstring, disallowed-name

from __future__ import annotations

import pytest

from frplib.exceptions import ConstructionError, KindError
from frplib.kinds      import (Kind, binary, choice, conditional_kind, constant,
                               given, kind, weighted_as, uniform)
from frplib.statistics import __


k1 = binary()
k2 = uniform(1, 2, ..., 8)
k3 = weighted_as(1, 10, 100, weights=[2, 5, 3])

def test_kind_proc_ijoin():
    @kind
    def ijoin1():
        x = yield k1
        y = yield k2
        return (x, y)

    @kind
    def ijoin2():
        x = yield k1
        y = yield k2
        z = yield k3
        return (x, y, z)

    @kind
    def ijoin3():
        x = yield choice(1, 2)
        y = yield choice(1, 2)
        z = yield choice(1, 2)
        return (x, y, z)

    assert Kind.equal(ijoin1, k1 * k2)
    assert Kind.equal(ijoin2, k1 * k2 * k3)
    assert Kind.equal(ijoin3, choice(1, 2) ** 3)

def test_kind_proc_trans():
    @kind
    def trans1():
        x = yield k3
        return x * x

    assert Kind.equal(trans1, k3 ^ (__ ** 2))

def test_kind_proc_obs():
    @kind
    def obs1():
        x = yield k2
        yield given(x % 2 == 0)
        return x

    assert Kind.equal(obs1, uniform(2, 4, 6, 8))

def test_kind_proc_gjoin():
    ck = conditional_kind({0: uniform(1, 2, 3), 1: weighted_as(-2, 0, 2, weights=[7, 2, 7])})

    @kind
    def join1():
        x = yield k1
        y = yield ck.target(x)   # ATTN: change to ck(x) when target/joined are swapped
        return (x, y)

    @kind
    def join2():
        x = yield k1
        y = yield ck.target(x)   # ATTN: change to ck(x) when target/joined are swapped
        return y

    assert Kind.equal(join1, k1 >> ck)
    assert Kind.equal(join2, ck // k1)

def test_kind_proc_errors():
    with pytest.raises(ConstructionError, match=r'no required positional arguments'):
        @kind                    # type: ignore
        def foo(_u):
            x = yield k1
            return x + 1

    @kind
    def args_ok(u=10):           # Args with defaults OK
        x = yield constant(9)
        return x + u

    assert Kind.equal(args_ok, constant(19))

    with pytest.raises(KindError, match=r'should be a Kind'):
        @kind
        def bar():
            x = yield 17
            return x + 1
