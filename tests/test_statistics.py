# pylint: disable=too-many-statements, too-many-function-args, line-too-long, invalid-name, missing-function-docstring, expression-not-assigned

from __future__ import annotations

import math
import pytest

from hypothesis             import given
from hypothesis.strategies  import integers, lists, floats

from frplib.exceptions import DomainDimensionError, InputError, MismatchedDomain, StatisticError
from frplib.kinds      import Kind, choice
from frplib.numeric    import nothing
from frplib.statistics import (is_statistic, statistic,
                               tuple_safe, infinity, is_true, is_false, scalar_fn,
                               Id, Scalar, __,
                               Sum, Count, Product, Max, Min, Mean, Abs,
                               Sqrt, Floor, Ceil,
                               Exp, Log, Log2, Log10,
                               Sin, Cos, Tan, ASin, ACos, ATan2, Sinh, Cosh, Tanh,
                               FromDegrees, FromRadians,
                               ArgMax, ArgMin,
                               Diff, SumSq, Norm, Ascending, Descending,
                               Constantly, Diffs, Proj, Permute, Dot,
                               Chain, Compose, Fork, ForEach, ForEachIndexed, IfThenElse,
                               And, Or, Not, Xor, All, Any, top, bottom,
                               Cases,
                               Median, Quartiles, IQR, Binomial, Distinct,
                               Get, ElementOf, Keep, MaybeMap,
                               Prepend, Append, Bag,
                               )
from frplib.quantity   import as_quantity, tup
from frplib.symbolic   import symbol
from frplib.utils      import codim, dim, identity, irange
from frplib.vec_tuples import VecTuple, as_vec_tuple, vec_tuple


def test_simple_builtin_statistics():
    assert Id(2) == tup(2)
    assert Id(100, 200) == tup(100, 200)
    assert Id(3, 4, 5) == tup(3, 4, 5)
    assert Id() == tup()

    assert (2 * __)(1) == tup(2)
    assert (2 * __)((1,)) == tup(2)
    assert (2 * __)((1, 2, 3)) == tup(2, 4, 6)

    assert Scalar(2) == tup(2)
    assert Scalar(100) == tup(100)
    with pytest.raises(DomainDimensionError):
        Scalar(2, 4)
    with pytest.raises(DomainDimensionError):
        Scalar((2, 4))

    assert is_true(top())
    assert is_true(top(1))
    assert is_true(top(1, 2, 3, 4))
    assert is_false(bottom())
    assert is_false(bottom(1))
    assert is_false(bottom(1, 2, 3, 4))

    assert Sum((1, 2, 3, 4, 5)) == tup(15)
    assert Sum(10, 20, 30, 40) == tup(100)
    assert Count((1, 2, 3, 4, 5)) == tup(5)
    assert Count(1, 1, 1, 1) == tup(4)
    assert Max((1, 2, 3, 4, 5)) == tup(5)
    assert Min((1, 2, 3, 4, 5)) == tup(1)
    assert Max(-10, 20, -3, 40, -500) == tup(40)
    assert Min(-10, 20, -3, 40, -500) == tup(-500)
    assert Mean(1, 2, 3, 4, 5) == tup(3)
    assert Mean(0) == tup(0)

    assert Sum() == tup(0)
    assert Count() == tup(0)
    assert Product() == tup(1)
    assert Min() == tup('infinity')
    assert Max() == tup('-infinity')

    assert Abs(-1) == tup(1)
    assert Abs(1) == tup(1)
    assert Abs(0) == tup(0)
    assert Abs(tup(0 for _ in range(10))) == tup(0)
    assert Abs(1, 1, 1, 1) == tup(2)
    assert Norm(1, 1, 1, 1) == tup(2)
    assert SumSq(1, 1, 1, 1) == tup(4)
    assert Abs(1, -1, 1, -1) == tup(2)
    assert Norm(1, 1, -1, -1) == tup(2)
    assert SumSq(1, -1, -1, -1) == tup(4)

    assert ArgMax(9, 1, 2, 8, 7) == tup(0)
    assert ArgMax(1, 32, 8, 7) == tup(1)
    assert ArgMax(-4, -9, -2, -1) == tup(3)
    assert ArgMin(9, 1, 2, 8, 7) == tup(1)
    assert ArgMin(1, 32, 8, 7) == tup(0)
    assert ArgMin(-4, -9, -2, -100) == tup(3)

    assert Ascending(10, 1, -2, 4, 0) == tup(-2, 0, 1, 4, 10)
    assert Descending(10, 1, -2, 4, 0) == tup(10, 4, 1, 0, -2)
    assert Ascending(1, 2, nothing, 4, -4) == tup(nothing, -4, 1, 2, 4)
    assert Descending(1, 2, nothing, 4, -4) == tup(4, 2, 1, -4, nothing)

    assert Diff((1, 2, 3, 4, 5)) == tup(1, 1, 1, 1)
    assert Diff(tup(irange(1, 11, step=2))) == tup(2 for _ in range(5))
    assert Diff(tup(irange(1, 17, step=2)) ^ (__ ** 2)) == tup(8 * i for i in irange(1, 8))

    assert Floor(-4.2) == tup(-5)
    assert Ceil(-4.2) == tup(-4)
    assert Floor(4.2) == tup(4)
    assert Ceil(4.2) == tup(5)
    assert Floor(0) == tup(0)
    assert Ceil(0) == tup(0)

    assert Abs(-4.2) == tup(4.2)
    assert Abs('4.2') == Abs(4.2)

    assert Sqrt(4) == tup(2)
    assert Sqrt(1.44) == tup(as_quantity(1.2))

    assert Log(1)[0] == pytest.approx(0)
    assert Log2(1)[0] == pytest.approx(0)
    assert Log10(1)[0] == pytest.approx(0)
    assert Log(Exp(1))[0] == pytest.approx(1)
    assert Log2(2)[0] == pytest.approx(1)
    assert Log10(10)[0] == pytest.approx(1)
    assert Log(Exp(4))[0] == pytest.approx(4)
    assert Log2(16)[0] == pytest.approx(4)
    assert Log10(10000)[0] == pytest.approx(4)

    with pytest.raises(StatisticError):
        Sqrt(-1)

    with pytest.raises(StatisticError):
        Log(-1)

    with pytest.raises(StatisticError):
        Log2(-1)

    with pytest.raises(StatisticError):
        Log10(-1)

    assert Sin(FromDegrees(30)) == as_quantity(0.5)
    assert Cos(1)[0] == pytest.approx(as_quantity(math.cos(1)))
    assert Sin(1)[0] == pytest.approx(as_quantity(math.sin(1)))
    assert Tan(FromDegrees(45))[0] == pytest.approx(as_quantity(1))

    assert math.isclose(FromRadians(ACos(0.5))[0], 60)
    assert math.isclose(FromRadians(ASin(0.5))[0], 30)
    assert math.isclose(FromRadians(ACos(0))[0], 90)
    assert math.isclose(FromRadians(ASin(0))[0], 0)
    assert math.isclose(FromRadians(ATan2(1, 1))[0], 45)
    assert math.isclose(FromRadians(ATan2(-1, 1))[0], -45)

def test_projections():
    assert Proj[1](10, 20, 30, 40, 50, 60, 70, 80) == tup(10)
    assert Proj[2](10, 20, 30, 40, 50, 60, 70, 80) == tup(20)
    assert Proj[3](10, 20, 30, 40, 50, 60, 70, 80) == tup(30)
    assert Proj[-1](10, 20, 30, 40, 50, 60, 70, 80) == tup(80)
    assert Proj[3:6](10, 20, 30, 40, 50, 60, 70, 80) == tup(30, 40, 50)
    assert Proj[3:-2](10, 20, 30, 40, 50, 60, 70, 80) == tup(30, 40, 50, 60)
    assert Proj[-3:](10, 20, 30, 40, 50, 60, 70, 80) == tup(60, 70, 80)
    assert Proj[:](10, 20, 30, 40, 50, 60, 70, 80) == tup(10, 20, 30, 40, 50, 60, 70, 80)
    assert Proj[1, 2, 4, 8](10, 20, 30, 40, 50, 60, 70, 80) == tup(10, 20, 40, 80)
    assert Proj[-7, -5, -3, -1](10, 20, 30, 40, 50, 60, 70, 80) == tup(20, 40, 60, 80)

def test_statistic_factories():
    c1 = Constantly(1)
    assert c1() == tup(1)
    assert c1(9) == tup(1)
    assert c1(-10, 33) == tup(1)
    assert c1(1.2, 3.5, 68, 9) == tup(1)
    assert c1(tup(irange(1, 100))) == tup(1)

    c12 = Constantly((1, 2))
    assert c12() == tup(1, 2)
    assert c12(9) == tup(1, 2)
    assert c12(-10, 33) == tup(1, 2)
    assert c12(1.2, 3.5, 68, 9) == tup(1, 2)
    assert c12(tup(irange(1, 100))) == tup(1, 2)

    c1234 = Constantly(1, 2, 3, 4)
    assert c1234() == tup(1, 2, 3, 4)
    assert c1234(9) == tup(1, 2, 3, 4)
    assert c1234(-10, 33) == tup(1, 2, 3, 4)
    assert c1234(1.2, 3.5, 68, 9) == tup(1, 2, 3, 4)
    assert c1234(tup(irange(1, 100))) == tup(1, 2, 3, 4)

    assert Permute(1, 4, 2, 3)(10, 20, 30, 40, 50, 60, 70) == tup(10, 40, 20, 30, 50, 60, 70)

    p1 = Permute(4, 2, 7, 3, 1, 5)
    p2 = Permute(4, 2, 7, 3, 1, 5, 6, cycle=False)

    assert p1(1, 2, 3, 4, 5, 6, 7, 8) == tup(3, 4, 7, 2, 1, 6, 5, 8)
    assert p2(1, 2, 3, 4, 5, 6, 7, 8) == tup(4, 2, 7, 3, 1, 5, 6, 8)
    assert Permute(2, 1)(1, 2, 3) == tup(2, 1, 3)
    assert Permute(2, 1, cycle=False)(1, 2, 3) == tup(2, 1, 3)

    assert Dot(1, 2, 3)(1, 2, 3) == tup(14)
    assert Dot(1, 2, 3)(1, 1, 1) == tup(6)

    assert Diffs(2)((1, 2, 3, 4, 5)) == tup(0, 0, 0)

    f = Cases({-1: 10, 1: 200, 3: 5}, default=0)
    assert f(-1) == tup(10)
    assert f(1) == tup(200)
    assert f(3) == tup(5)
    assert f(9) == tup(0)

    g = Cases({(1, 2): (3, 4), (5, 6): (7, 8), (9, 10): (11, 12)})
    assert g(1, 2) == tup(3, 4)
    assert g(5, 6) == tup(7, 8)
    assert g(9, 10) == tup(11, 12)

    assert Cases({}, 0)(10) == 0

    with pytest.raises(MismatchedDomain):
        g(9, 9)

    with pytest.raises(DomainDimensionError):
        Cases({(1, 2): (3, 4), (5, 6): (7, 8), (9, 10): (11, 12, 13)})


def test_more_factories():
    a_list = [2 * k + 100 for k in range(25)]
    a_dict = {k: 2 * k - 100 for k in range(25)}
    b_dict = {(k, k + 10): tup(k, k + 2, k + 8) for k in range(25)}

    for k in range(25):
        assert Get(a_list)(k) == tup(2 * k + 100)
        assert Get(a_dict)(k) == tup(2 * k - 100)
        assert Get(b_dict)(k, k + 10) == tup(k, k + 2, k + 8)

    s = ElementOf(43, 93, 103)
    assert s(43) == tup(1)
    assert s(93) == tup(1)
    assert s(103) == tup(1)
    for k in irange(1, 110, exclude={43, 93, 103}):
        assert s(k) == tup(0)

    assert Prepend(1, 2, 3)(10, 20, 30) == tup(1, 2, 3, 10, 20, 30)
    assert Prepend(1, 2)(10, 20, 30) == tup(1, 2, 10, 20, 30)
    assert Prepend(1)(10, 20, 30) == tup(1, 10, 20, 30)
    assert Prepend()(10, 20, 30) == tup(10, 20, 30)
    assert Append(1, 2, 3)(10, 20, 30) == tup(10, 20, 30, 1, 2, 3)
    assert Append(1, 2)(10, 20, 30) == tup(10, 20, 30, 1, 2)
    assert Append(1)(10, 20, 30) == tup(10, 20, 30, 1)
    assert Append()(10, 20, 30) == tup(10, 20, 30)

    assert Bag(1, 2, 3, 4) == tup(1, 1, 2, 1, 3, 1, 4, 1)
    assert Bag(1, 2, 3, 4, 3) == tup(1, 1, 2, 1, 3, 2, 4, 1)
    assert Bag(1, 2, 1, 1, 3, 4, 3) == tup(1, 3, 2, 1, 3, 2, 4, 1)
    assert Bag(2, 4, 4, 1, 2, 1, 1, 4, 3, 4, 4, 4, 3, 2, 2) == tup(1, 3, 2, 4, 3, 2, 4, 6)

    bc5 = [1, 5, 10, 10, 5, 1]
    for j in range(6):
        assert Binomial(5, j) == tup(bc5[j])
    assert Binomial(20, 10) == tup(184756)
    assert Binomial(1.2, 0) == tup(1)
    assert Binomial(20, 0) == tup(1)
    assert Binomial(20, -1) == tup(0)
    for j in range(10):
        assert Binomial(-1, j) == tup((-1) ** j)
    assert Binomial(2.5, 4)[0] == pytest.approx(as_quantity('-0.039062500000000014'))

    assert Keep(Scalar % 2 == 0)(1, 2, 3, 4) == tup(2, 4, nothing, nothing)
    assert Keep(Scalar % 2 == 0, pad=-1)(1, 2, 3, 4) == tup(2, 4, -1, -1)
    assert Keep(__ > 0, pad=0)(-20, 2, -2, 10, 20) == tup(2, 10, 20, 0, 0)

    def Nu(cond, stat=Id):  # NothingUnless
        return IfThenElse(cond, stat, nothing)

    assert MaybeMap(Nu(Scalar % 2 == 0))(1, 2, 3, 4) == tup(2, 4, nothing, nothing)
    assert MaybeMap(Nu(Scalar % 2 != 0, 1), pad=-1)(1, 2, 3, 4) == tup(1, 1, -1, -1)

    odd_double = Nu(Scalar % 2 != 0, 2 * __)
    assert MaybeMap(odd_double, pad=-1)(1, 2, 3, 4) == tup(2, 6, -1, -1)

    pos_square = IfThenElse(__ > 0, __ ** 2, nothing)
    assert MaybeMap(pos_square, pad=0)(-20, 2, -2, 10, 20) == tup(4, 100, 400, 0, 0)

    @statistic(codim=1, dim=3)
    def repeat3(v):
        if v > 0:
            return (v, v, v)
        return nothing

    assert MaybeMap(repeat3)(1, 4, 10) == tup(1, 1, 1, 4, 4, 4, 10, 10, 10)
    assert MaybeMap(repeat3)(1, -4, 4, 0, 10) == tup(1, 1, 1, 4, 4, 4, 10, 10, 10, nothing, nothing, nothing, nothing, nothing, nothing)
    assert MaybeMap(repeat3, pad=None)(1, -4, 4, 0, 10) == tup(1, 1, 1, 4, 4, 4, 10, 10, 10)

def test_statistic_combinators():
    assert tup(-1, -10, 1, 2) ^ Chain(Sum, Abs) == tup(8)
    assert tup(-1, -10, 1, 2) ^ Compose(Abs, Sum) == tup(8)

    assert ForEach(__ % 2)(1, 2, 3, 4) == tup(1, 0, 1, 0)
    assert ForEach(__ % 2 == 0)(1, 2, 3, 4) == tup(0, 1, 0, 1)

    assert IfThenElse(Proj[1](__) == 2, 2 * __, __ + 10)(11, 12, 13) == tup(21, 22, 23)
    assert IfThenElse(__ % 2 == 0, 0, __ + 1)(11) == tup(12)
    assert IfThenElse(__ % 2 == 0, 0, __ + 1)(10) == tup(0)
    assert IfThenElse(Scalar > 0, 1, IfThenElse(__ < 0, -1, 0))(10) == tup(1)
    assert IfThenElse(Scalar > 0, 1, IfThenElse(__ < 0, -1, 0))(0) == tup(0)
    assert IfThenElse(Scalar > 0, 1, IfThenElse(__ < 0, -1, 0))(-99) == tup(-1)

    assert Fork(__, Constantly(2), __ ** 2)(1) == tup(1, 2, 1)
    assert Fork(__, Constantly(2), __ ** 2)((1,)) == tup(1, 2, 1)
    assert Fork(__, Constantly(2), __ ** 2)((1, 2, 3)) == tup(1, 2, 3, 2, 1, 4, 9)

    assert Fork(Id, 2, __ ** 2)(4) == tup(4, 2, 16)
    assert Fork(identity, 2, __ ** 2)(4) == tup(4, 2, 16)
    assert Fork(__ + 1, __ + 2, __ + 3)(10, 20) == tup(11, 21, 12, 22, 13, 23)
    assert tup(10, 20, 30, 40) ^ Fork(Id, 1, Sum) == tup(10, 20, 30, 40, 1, 100)
    assert tup(10, 20, 40) ^ Fork(Sum, Diff) == tup(70, 10, 20)

    assert ForEach(__ ** 2)(1, 2, 3) == tup(1, 4, 9)
    assert ForEach(9)(1, 2, 3) == tup(9, 9, 9)

    assert tup(-10, 20, -3) ^ ForEach(Abs) == tup(10, 20, 3)
    assert tup() ^ ForEach(Sin) == tup()
    assert ForEach(__ ** 2)(1, 2, 3) == tup(1, 4, 9)
    assert ForEach(__ + 3)(1, 2, 3) == tup(4, 5, 6)
    assert ForEach(1)(1, 2, 3, 4) == tup(1, 1, 1, 1)
    assert ForEach((1, 2, 3))(10, 11, 12) == tup(1, 2, 3, 1, 2, 3, 1, 2, 3)

    assert tup(irange(1, 8)) ^ ForEach(Proj[4]) == tup(4, 8)
    assert tup(irange(1, 8)) ^ ForEach(Proj[1], by=4) == tup(1, 5)
    assert tup(irange(1, 8)) ^ ForEach(Proj[2], by=4) == tup(2, 6)
    assert tup(irange(1, 8)) ^ ForEach(Proj[3], by=4) == tup(3, 7)
    assert tup(irange(1, 12)) ^ ForEach(Permute(3, 1, 2)) == tup(3, 1, 2, 6, 4, 5, 9, 7, 8, 12, 10, 11)

    swap = statistic(lambda x, y: (y, x), dim=2, description='swaps two components of a pair')
    assert tup(irange(1, 8)) ^ ForEach(swap) == tup(2, 1, 4, 3, 6, 5, 8, 7)
    assert tup(-1, 0, 1, 2, -3, 0, 0, 1, 1) ^ ForEach(Sum, by=3) == tup(0, -1, 2)

    assert ForEachIndexed(__ ** 2)(1, 2, 3) == tup(0, 1, 1, 4, 4, 9)
    assert ForEachIndexed(__ + 3)(1, 2, 3) == tup(3, 4, 4, 5, 5, 6)
    assert ForEachIndexed(1)(1, 2, 3, 4) == tup(1, 1, 1, 1)
    assert ForEachIndexed(swap)(11, 21, 31, 41) == tup(11, 0, 21, 1, 31, 2, 41, 3)

    with pytest.raises(StatisticError):
        tup(irange(1, 9)) ^ ForEach(swap, by=3)

    with pytest.raises(StatisticError):
        tup(irange(1, 9)) ^ ForEach(swap)

    with pytest.raises(StatisticError):
        tup(irange(1, 9)) ^ ForEach(swap, strict=False)

    assert tup(irange(1, 9)) ^ ForEach(Sum, by=2, strict=False) == tup(3, 7, 11, 15, 9)
    assert tup(irange(1, 8)) ^ ForEach(Sum, by=2) == tup(3, 7, 11, 15)

    k = choice(0, 1) ** 4
    assert Kind.equal(k ^ Proj[1, 2] ^ Sum, k ^ (Proj[1, 2] ^ Sum))
    assert is_statistic(Proj[1, 2] ^ Sum)
    assert codim(Proj[1, 2] ^ Sum) == (2, infinity)
    assert dim(Proj[1, 2] ^ Sum) == 1

def test_condition_combinators():
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(-12, 21) == tup(1)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(-11, 21) == tup(0)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(-11, -21) == tup(0)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(0, -21) == tup(0)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(0, 0) == tup(0)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(2, 2) == tup(1)

    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(-12, 21) == tup(1)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(-11, 21) == tup(1)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(-11, -21) == tup(0)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(0, -21) == tup(1)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(0, 0) == tup(1)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(1, 1) == tup(1)

    assert Not(Proj[1] % 2 == 0)(2) == tup(0)
    assert Not(Proj[1] % 2 == 0)(3) == tup(1)
    assert Not(Proj[1] % 2 == 0)(5) == tup(1)
    assert Not(Proj[1] % 2 == 0)(8) == tup(0)
    assert Not(Proj[1] % 2 == 0)(2, 7) == tup(0)
    assert Not(Proj[1] % 2 == 0)(3, 9) == tup(1)
    assert Not(Proj[1] % 2 == 0)(5, 9, 10) == tup(1)
    assert Not(Proj[1] % 2 == 0)(8, 3, 2, 1) == tup(0)

    assert Xor(Proj[1] % 2 == 0, Proj[2] > 0)(0, 0) == tup(1)
    assert Xor(Proj[1] % 2 == 0, Proj[2] > 0)(1, 1) == tup(1)
    assert Xor(Proj[1] % 2 == 0, Proj[2] > 0)(0, 1) == tup(0)
    assert Xor(Proj[1] % 2 == 0, Proj[2] > 0)(4, 1) == tup(0)

    assert All(__ == 2)(2, 2, 2, 2) == tup(1)
    assert All(__ == 2)(2, 2, 3, 2) == tup(0)
    assert Any(__ == 2)(2, 2, 3, 2) == tup(1)
    assert Any(__ == 7)(2, 2, 3, 2) == tup(0)

    assert is_true(tup(1))
    assert not is_true(tup(0))
    assert is_false(tup(0))
    assert not is_false(tup(1))
    assert is_true(Abs(2, 2, 2, 2) >= 4)
    assert not is_true(Abs(2, 2, 2, 2) >= 4.1)
    assert not is_false(Abs(2, 2, 2, 2) >= 4)
    assert is_false(Abs(2, 2, 2, 2) >= 4.1)

    with pytest.raises(StatisticError):
        is_true(tup(1, 2))

    with pytest.raises(StatisticError):
        is_true(tup())

def test_statistic_expressions():
    a = symbol('a')
    assert str((1 + 2 * __ + 3 * __ ** 2)(a)) == '<1 + 2 a + 3 a^2>'

    assert (2 ** __)(1, 2, 3) == tup(2, 4, 8)
    assert (__ ** 2)(1, 2, 3) == tup(1, 4, 9)
    assert (__ % 2 == 0)(4) == tup(1)

def test_tuple_safe():
    def sc_fn(x):
        return as_quantity(x) + 1

    s1 = tuple_safe(sc_fn, arities=1, strict=False)
    s1s = tuple_safe(sc_fn, arities=1, strict=True)

    assert s1(4) == tup(5)
    assert s1((4,)) == tup(5)
    assert s1(-1) == tup(0)
    assert s1('1/2') == tup(1.5)
    assert s1(17, 10) == tup(18)
    assert s1((17, 10)) == tup(18)
    assert s1((-101, 1, 2, 3, 4, 5)) == tup(-100)

    with pytest.raises(DomainDimensionError):
        s1s(17, 10)

    with pytest.raises(DomainDimensionError):
        s1s((17, 10))

    with pytest.raises(DomainDimensionError):
        s1s()

    with pytest.raises(DomainDimensionError):
        s1s((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))

    def bad_1(x, y, z):
        return x + y + z

    with pytest.raises(InputError):
        tuple_safe(bad_1, arities=(1, 3), strict=False)

    with pytest.raises(InputError):
        tuple_safe(bad_1, arities=4, strict=False)

    with pytest.raises(InputError):
        tuple_safe(bad_1, arities=(0, infinity), strict=False)

    def v_fn(a, b, c):
        return (a, b, c, 0)

    v1 = tuple_safe(v_fn, strict=False)
    v1s = tuple_safe(v_fn, strict=True)

    assert v1(1, 2, 3) == tup(1, 2, 3, 0)
    assert v1((1, 2, 3)) == tup(1, 2, 3, 0)
    assert v1((1, 2, 3, 4, 5, 6, 7, 8)) == tup(1, 2, 3, 0)

    with pytest.raises(DomainDimensionError):
        v1s((1, 2, 3, 4))

    with pytest.raises(DomainDimensionError):
        v1(1, 2)

    with pytest.raises(DomainDimensionError):
        v1s(1, 2)

    with pytest.raises(DomainDimensionError):
        v1((4,))

    with pytest.raises(DomainDimensionError):
        v1()

    def vt_fn(a):
        u, v, w = a
        return (u, v, w, 0)

    v2 = tuple_safe(vt_fn, arities=3, strict=False)
    v2s = tuple_safe(vt_fn, arities=3, strict=True)

    assert v2(1, 2, 3) == tup(1, 2, 3, 0)
    assert v2((1, 2, 3)) == tup(1, 2, 3, 0)
    assert v2((1, 2, 3, 4, 5, 6, 7, 8)) == tup(1, 2, 3, 0)

    with pytest.raises(DomainDimensionError):
        v2s((1, 2, 3, 4))

    with pytest.raises(DomainDimensionError):
        v2((1, 2,))

    with pytest.raises(DomainDimensionError):
        v2(1, 2,)

    with pytest.raises(DomainDimensionError):
        v2()

    def vm_fn(a):
        return sum(a[2:])

    v3 = tuple_safe(vm_fn, arities=(3, infinity), strict=False)
    assert v3(1, 2, 3, 4) == tup(7)
    assert v3(tuple(range(11))) == tup(54)
    assert v3(10, 90, 80) == tup(80)

    with pytest.raises(DomainDimensionError):
        v3((1, 2))
    with pytest.raises(DomainDimensionError):
        v3(4)
    with pytest.raises(DomainDimensionError):
        v3()

    with pytest.raises(DomainDimensionError):
        Proj[1, 2, 4](1, 2)
    with pytest.raises(DomainDimensionError):
        Proj[1, 2, 4]((1, 2))

    assert codim(Proj[1, 2, 4]) == (4, infinity)
    assert codim(Proj[2]) == (2, infinity)
    assert codim(Proj[-2, -1]) == (0, infinity)

def test_stat_dims():
    "tests inference of statistics' dimensions with various combinators and factories"
    u = statistic(lambda x: (x, x, x, 1), codim=1, dim=4)
    v = statistic(lambda x: (x + 1, x + 2, x + 3, x + 4), codim=1, dim=4)
    w = Constantly(12)
    z = statistic(lambda x: 2 * x)

    assert dim(u) == 4
    assert dim(v) == 4
    assert dim(w) == 1
    assert dim(z) is None

    assert dim(u + v) == 4
    assert dim(u - v) == 4
    assert dim(u * v) == 4
    assert dim(u / v) == 4
    assert dim(u // v) == 4
    assert dim(u % v) == 4
    assert dim(u ** v) == 4

    assert dim(u * w) == 4
    assert dim(u / w) == 4
    assert dim(u // w) == 4
    assert dim(u % w) == 4
    assert dim(u ** w) == 4

    assert dim(w * u) == 4
    assert dim(w / u) == 4
    assert dim(w // u) == 4
    assert dim(w % u) == 4
    assert dim(w ** u) == 4

    assert dim(u * z) is None
    assert dim(u / z) is None
    assert dim(u // z) is None
    assert dim(u % z) is None
    assert dim(u ** z) is None

    assert dim(z * u) is None
    assert dim(z / u) is None
    assert dim(z // u) is None
    assert dim(z % u) is None
    assert dim(z ** u) is None

    assert dim(Proj[1]) == 1
    assert dim(Proj[4]) == 1
    assert codim(Proj[4]) == (4, infinity)
    assert dim(Proj[1, 3]) == 2
    assert codim(Proj[1, 3]) == (3, infinity)
    assert dim(Proj[1, 3, 5]) == 3
    assert codim(Proj[1, 3, 5]) == (5, infinity)
    assert dim(Proj[1, 3, 5, 7, 9, 10, 100]) == 7

    assert dim(Proj[:4]) == 3
    assert dim(Proj[:4:2]) == 2
    assert dim(Proj[3:10]) == 7
    assert dim(Proj[3:10:2]) == 4
    assert dim(Proj[18:10:-2]) == 4
    assert dim(Proj[18:1:-1]) == 17
    assert dim(Proj[18::-1]) == 18
    assert dim(Proj[-4:-2]) is None
    assert dim(Proj[2:-3]) is None
    assert dim(Proj[-2:10]) is None

    assert dim(Fork(u, v, w)) == 9
    assert dim(Fork(u, v, z)) is None
    assert codim(Fork(u, v, w)) == (1, 1)
    assert codim(Fork(u, v, z)) == (1, 1)

def test_scalar_fn():
    "test scalar_fn utility in statistics, see Issue 48"
    am = scalar_fn(ArgMax)

    assert am(1, 9, 2) == 1
    assert am((1, 9, 2)) == 1
    assert am(vec_tuple(1, 9, 2)) == 1
    assert am(1, 9, 2, 7, 17, 21, 3) == 5
    assert am((14, 22, 32, -4, 0)) == 2
    assert am(14, 22, 32, -4, 0) == 2

@given(floats(min_value=-4 * math.pi, max_value=4 * math.pi))
def test_trig_statistics(x):
    assert Cos(x)[0] == pytest.approx(as_quantity(math.cos(x)))
    assert Sin(x)[0] == pytest.approx(as_quantity(math.sin(x)))
    assert Tan(x)[0] == pytest.approx(as_quantity(math.tan(x)))

    assert Cosh(x)[0] == pytest.approx(as_quantity(math.cosh(x)))
    assert Sinh(x)[0] == pytest.approx(as_quantity(math.sinh(x)))
    assert Tanh(x)[0] == pytest.approx(as_quantity(math.tanh(x)))

    assert Scalar(Sin ** 2 + Cos ** 2)(x)[0] == pytest.approx(1)
    assert Scalar(Sin(2 * __) - 2 * Sin(__) * Cos(__))(x)[0] == pytest.approx(0)

    assert FromDegrees(FromRadians(x))[0] == pytest.approx(as_quantity(x))

def int_value_gen(max_dim):
    return lists(integers(min_value=-1024, max_value=1024),
                 min_size=1, max_size=max_dim).map(as_vec_tuple)

@given(int_value_gen(16))
def test_median_distinct(v):
    n = len(v)
    sv = sorted(v)
    if n % 2 == 0:
        med = Median(v)
        assert med == tup((sv[(n - 1) // 2] + sv[n // 2]) / 2)
        if n >= 4:
            q = Quartiles(v)
            assert q[0] == Median(VecTuple.join(sv[:(n // 2)], med))
            assert q[2] == Median(VecTuple.join(sv[(n // 2):], med))
    else:
        assert Median(v) == tup(sv[n // 2])
        if n >= 4:
            q = Quartiles(v)
            assert q[0] == Median(*sv[:(n // 2)])
            assert q[2] == Median(*sv[((n // 2) + 1):])

    assert Distinct(v) == tup(1 if len(set(v)) == n else 0)

    assert Median((64, 77, 78, 82, 85, 92, 95)) == 82
    assert IQR((64, 77, 78, 82, 85, 92, 95)) == 15     # type 6 IQR excludes median
