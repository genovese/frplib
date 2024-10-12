from __future__ import annotations

import math
import pytest

from hypothesis             import given
from hypothesis.strategies  import integers, decimals, tuples, lists, one_of, dictionaries

from frplib.exceptions import DomainDimensionError, InputError, MismatchedDomain
from frplib.kinds      import Kind, either
from frplib.numeric    import nothing
from frplib.statistics import (Statistic, Condition, MonoidalStatistic,
                               is_statistic, statistic, condition, scalar_statistic,
                               tuple_safe, infinity, ANY_TUPLE,
                               chain, compose,
                               Id, Scalar, __, Proj, _x_,
                               Sum, Count, Product, Max, Min, Mean, Abs,
                               Sqrt, Floor, Ceil,
                               Exp, Log, Log2, Log10,
                               Sin, Cos, Tan, ATan2, Sinh, Cosh, Tanh,
                               FromDegrees, FromRadians,
                               Diff, Diffs, Permute,
                               SumSq, Norm, Dot, Ascending, Descending,
                               Constantly, Fork, ForEach, IfThenElse,
                               And, Or, Not, Xor, top, bottom,
                               Cases, All, Any, ACos, ASin,
                               Median, Quartiles, Binomial, Distinct,
                               Get, ElementOf, Keep, MaybeMap,
                               Prepend, Append, Bag,
                               )
from frplib.quantity   import as_quantity, qvec
from frplib.symbolic   import symbol
from frplib.utils      import codim, dim, identity, irange
from frplib.vec_tuples import as_vec_tuple, vec_tuple, join


def test_builtin_statistics():
    "Builtin statistics and combinators."

    assert Id(2) == vec_tuple(2)
    assert Id(100, 200) == vec_tuple(100, 200)
    assert Id(3, 4, 5) == vec_tuple(3, 4, 5)
    assert Id() == vec_tuple()

    assert (2 * __)(1) == vec_tuple(2)
    assert (2 * __)((1,)) == vec_tuple(2)
    assert (2 * __)((1, 2, 3)) == vec_tuple(2, 4, 6)

    assert Scalar(2) == vec_tuple(2)
    assert Scalar(100) == vec_tuple(100)
    with pytest.raises(DomainDimensionError):
        Scalar(2, 4)
    with pytest.raises(DomainDimensionError):
        Scalar((2, 4))

    assert (2 ** __)(1, 2, 3) == vec_tuple(2, 4, 8)
    assert (__ ** 2)(1, 2, 3) == vec_tuple(1, 4, 9)
    assert (__ % 2 == 0)(4) == vec_tuple(1)
    assert ForEach(__ % 2)(1, 2, 3, 4) == vec_tuple(1, 0, 1, 0)
    assert ForEach(__ % 2 == 0)(1, 2, 3, 4) == vec_tuple(0, 1, 0, 1)

    assert IfThenElse(Proj[1](__) == 2, 2 * __, __ + 10)(11, 12, 13) == vec_tuple(21, 22, 23)

    assert Fork(__, Constantly(2), __ ** 2)(1) == vec_tuple(1, 2, 1)
    assert Fork(__, Constantly(2), __ ** 2)((1,)) == vec_tuple(1, 2, 1)
    assert Fork(__, Constantly(2), __ ** 2)((1, 2, 3)) == vec_tuple(1, 2, 3, 2, 1, 4, 9)

    assert Fork(Id, 2, __ ** 2)(4) == vec_tuple(4, 2, 16)
    assert Fork(identity, 2, __ ** 2)(4) == vec_tuple(4, 2, 16)
    assert Fork(__ + 1, __ + 2, __ + 3)(10, 20) == vec_tuple(11, 21, 12, 22, 13, 23)

    assert ForEach(__ ** 2)(1, 2, 3) == vec_tuple(1, 4, 9)
    assert ForEach(9)(1, 2, 3) == vec_tuple(9, 9, 9)

    assert Cos(1)[0] == pytest.approx(as_quantity(math.cos(1)))
    assert Sin(1)[0] == pytest.approx(as_quantity(math.sin(1)))

    assert Scalar(Sin ** 2 + Cos ** 2) == pytest.approx(1)

    assert Sum((1, 2, 3, 4, 5)) == vec_tuple(15)
    assert Count((1, 2, 3, 4, 5)) == vec_tuple(5)
    assert Max((1, 2, 3, 4, 5)) == vec_tuple(5)
    assert Min((1, 2, 3, 4, 5)) == vec_tuple(1)

    assert Sum() == vec_tuple(0)
    assert Count() == vec_tuple(0)
    assert Product() == vec_tuple(1)
    assert Min() == vec_tuple(as_quantity('infinity'))
    assert Max() == vec_tuple(as_quantity('-infinity'))

    assert Abs(-1) == vec_tuple(1)
    assert Abs(1) == vec_tuple(1)
    assert Abs(0) == vec_tuple(0)
    assert Abs(1, 1, 1, 1) == vec_tuple(2)
    assert Norm(1, 1, 1, 1) == vec_tuple(2)
    assert SumSq(1, 1, 1, 1) == vec_tuple(4)

    assert Dot(1, 2, 3)(1, 2, 3) == vec_tuple(14)
    assert Dot(1, 2, 3)(1, 1, 1) == vec_tuple(6)

    assert Ascending(10, 1, -2, 4, 0) == vec_tuple(-2, 0, 1, 4, 10)
    assert Descending(10, 1, -2, 4, 0) == vec_tuple(10, 4, 1, 0, -2)

    assert Diff((1, 2, 3, 4, 5)) == vec_tuple(1, 1, 1, 1)
    assert Diffs(2)((1, 2, 3, 4, 5)) == vec_tuple(0, 0, 0)

    a = symbol('a')
    assert str((1 + 2 * __ + 3 * __ ** 2)(a)) == '<1 + 2 a + 3 a^2>'

    assert Proj[1](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(10)
    assert Proj[2](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(20)
    assert Proj[3](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(30)
    assert Proj[-1](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(80)
    assert Proj[3:6](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(30, 40, 50)
    assert Proj[3:-2](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(30, 40, 50, 60)
    assert Proj[-3:](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(60, 70, 80)
    assert Proj[:](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(10, 20, 30, 40, 50, 60, 70, 80)
    assert Proj[1, 2, 4, 8](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(10, 20, 40, 80)
    assert Proj[-7, -5, -3, -1](10, 20, 30, 40, 50, 60, 70, 80) == vec_tuple(20, 40, 60, 80)

    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(-12, 21) == vec_tuple(1)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(-11, 21) == vec_tuple(0)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(-11, -21) == vec_tuple(0)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(0, -21) == vec_tuple(0)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(0, 0) == vec_tuple(0)
    assert And(Proj[1] % 2 == 0, Proj[2] > 0)(2, 2) == vec_tuple(1)

    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(-12, 21) == vec_tuple(1)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(-11, 21) == vec_tuple(1)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(-11, -21) == vec_tuple(0)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(0, -21) == vec_tuple(1)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(0, 0) == vec_tuple(1)
    assert Or(Proj[1] % 2 == 0, Proj[2] > 0)(1, 1) == vec_tuple(1)

    assert Not(Proj[1] % 2 == 0)(2) == vec_tuple(0)
    assert Not(Proj[1] % 2 == 0)(3) == vec_tuple(1)
    assert Not(Proj[1] % 2 == 0)(5) == vec_tuple(1)
    assert Not(Proj[1] % 2 == 0)(8) == vec_tuple(0)
    assert Not(Proj[1] % 2 == 0)(2, 7) == vec_tuple(0)
    assert Not(Proj[1] % 2 == 0)(3, 9) == vec_tuple(1)
    assert Not(Proj[1] % 2 == 0)(5, 9, 10) == vec_tuple(1)
    assert Not(Proj[1] % 2 == 0)(8, 3, 2, 1) == vec_tuple(0)

    assert Permute(1, 4, 2, 3)(10, 20, 30, 40, 50, 60, 70) == vec_tuple(10, 40, 20, 30, 50, 60, 70)

    assert Floor(-4.2) == vec_tuple(-5)
    assert Ceil(-4.2) == vec_tuple(-4)
    assert Floor(4.2) == vec_tuple(4)
    assert Ceil(4.2) == vec_tuple(5)
    assert Floor(0) == vec_tuple(0)
    assert Ceil(0) == vec_tuple(0)

    assert Abs(-4.2) == qvec(4.2)
    assert Abs('4.2') == Abs(4.2)

    assert Sqrt(4) == vec_tuple(2)
    assert Sqrt(1.44) == vec_tuple(as_quantity(1.2))

    assert Sin(FromDegrees(30)) == as_quantity(0.5)

    p1 = Permute(4, 2, 7, 3, 1, 5)
    p2 = Permute(4, 2, 7, 3, 1, 5, 6, cycle=False)

    assert p1(1, 2, 3, 4, 5, 6, 7, 8) == vec_tuple(3, 4, 7, 2, 1, 6, 5, 8)
    assert p2(1, 2, 3, 4, 5, 6, 7, 8) == vec_tuple(4, 2, 7, 3, 1, 5, 6, 8)
    assert Permute(2, 1)(1, 2, 3) == vec_tuple(2, 1, 3)
    assert Permute(2, 1, cycle=False)(1, 2, 3) == vec_tuple(2, 1, 3)


def test_more_builtins():
    f = Cases({-1: 10, 1: 200, 3: 5}, default=0)
    assert f(-1) == vec_tuple(10)
    assert f(1) == vec_tuple(200)
    assert f(3) == vec_tuple(5)
    assert f(9) == vec_tuple(0)

    g = Cases({(1, 2): (3, 4), (5, 6): (7, 8), (9, 10): (11, 12)})
    assert g(1, 2) == vec_tuple(3, 4)
    assert g(5, 6) == vec_tuple(7, 8)
    assert g(9, 10) == vec_tuple(11, 12)

    assert Cases({}, 0)(10) == 0

    with pytest.raises(MismatchedDomain):
        g(9, 9)

    with pytest.raises(DomainDimensionError):
        Cases({(1, 2): (3, 4), (5, 6): (7, 8), (9, 10): (11, 12, 13)})

    assert All(__ == 2)(2, 2, 2, 2) == vec_tuple(1)
    assert All(__ == 2)(2, 2, 3, 2) == vec_tuple(0)
    assert Any(__ == 2)(2, 2, 3, 2) == vec_tuple(1)
    assert Any(__ == 7)(2, 2, 3, 2) == vec_tuple(0)

    assert math.isclose(FromRadians(ACos(0.5))[0], 60)
    assert math.isclose(FromRadians(ASin(0.5))[0], 30)
    assert math.isclose(FromRadians(ACos(0))[0], 90)
    assert math.isclose(FromRadians(ASin(0))[0], 0)

def int_value_gen(max_dim):
    return lists(integers(min_value=-1024, max_value=1024),
                 min_size=1, max_size=max_dim).map(as_vec_tuple)

@given(int_value_gen(16))
def test_median_distinct(v):
    n = len(v)
    sv = sorted(v)
    if n % 2 == 0:
        med = Median(v)
        assert med == vec_tuple((sv[(n - 1) // 2] + sv[n // 2]) / 2)
        if n >= 4:
            q = Quartiles(v)
            assert q[0] == Median(join(sv[:(n // 2)], med))
            assert q[2] == Median(join(sv[(n // 2):], med))
    else:
        assert Median(v) == vec_tuple(sv[n // 2])
        if n >= 4:
            q = Quartiles(v)
            assert q[0] == Median(*sv[:(n // 2)])
            assert q[2] == Median(*sv[((n // 2) + 1):])

    assert Distinct(v) == vec_tuple(1 if len(set(v)) == n else 0)

def test_yet_more_builtins():
    a_list = [2 * k + 100 for k in range(25)]
    a_dict = {k: 2 * k - 100 for k in range(25)}
    b_dict = {(k, k + 10): vec_tuple(k, k + 2, k + 8) for k in range(25)}

    for k in range(25):
        assert Get(a_list)(k) == vec_tuple(2 * k + 100)
        assert Get(a_dict)(k) == vec_tuple(2 * k - 100)
        assert Get(b_dict)(k, k + 10) == vec_tuple(k, k + 2, k + 8)

    s = ElementOf(43, 93, 103)
    assert s(43) == vec_tuple(1)
    assert s(93) == vec_tuple(1)
    assert s(103) == vec_tuple(1)
    for k in irange(1, 110, exclude={43, 93, 103}):
        assert s(k) == vec_tuple(0)

    assert Prepend(1, 2, 3)(10, 20, 30) == vec_tuple(1, 2, 3, 10, 20, 30)
    assert Prepend(1, 2)(10, 20, 30) == vec_tuple(1, 2, 10, 20, 30)
    assert Prepend(1)(10, 20, 30) == vec_tuple(1, 10, 20, 30)
    assert Prepend()(10, 20, 30) == vec_tuple(10, 20, 30)
    assert Append(1, 2, 3)(10, 20, 30) == vec_tuple(10, 20, 30, 1, 2, 3)
    assert Append(1, 2)(10, 20, 30) == vec_tuple(10, 20, 30, 1, 2)
    assert Append(1)(10, 20, 30) == vec_tuple(10, 20, 30, 1)
    assert Append()(10, 20, 30) == vec_tuple(10, 20, 30)

    assert Bag(1, 2, 3, 4) == vec_tuple(1, 1, 2, 1, 3, 1, 4, 1)
    assert Bag(1, 2, 3, 4, 3) == vec_tuple(1, 1, 2, 1, 3, 2, 4, 1)
    assert Bag(1, 2, 1, 1, 3, 4, 3) == vec_tuple(1, 3, 2, 1, 3, 2, 4, 1)
    assert Bag(2, 4, 4, 1, 2, 1, 1, 4, 3, 4, 4, 4, 3, 2, 2) == vec_tuple(1, 3, 2, 4, 3, 2, 4, 6)

    bc5 = [1, 5, 10, 10, 5, 1]
    for j in range(6):
        assert Binomial(5, j) == vec_tuple(bc5[j])
    assert Binomial(20, 10) == vec_tuple(184756)
    assert Binomial(1.2, 0) == vec_tuple(1)
    assert Binomial(20, 0) == vec_tuple(1)
    assert Binomial(20, -1) == vec_tuple(0)
    for j in range(10):
        assert Binomial(-1, j) == vec_tuple((-1) ** j)
    assert Binomial(2.5, 4)[0] == pytest.approx(as_quantity('-0.039062500000000014'))

    assert Keep(Scalar % 2 == 0)(1, 2, 3, 4) == vec_tuple(2, 4, nothing, nothing)
    assert Keep(Scalar % 2 == 0, pad=-1)(1, 2, 3, 4) == vec_tuple(2, 4, -1, -1)
    assert Keep(__ > 0, pad=0)(-20, 2, -2, 10, 20) == vec_tuple(2, 10, 20, 0, 0)

    def Nu(cond, stat=Id):  # NothingUnless
        return IfThenElse(cond, stat, nothing)

    assert MaybeMap(Nu(Scalar % 2 == 0))(1, 2, 3, 4) == vec_tuple(2, 4, nothing, nothing)
    assert MaybeMap(Nu(Scalar % 2 != 0, 1), pad=-1)(1, 2, 3, 4) == vec_tuple(1, 1, -1, -1)

    odd_double = Nu(Scalar % 2 != 0, 2 * __)
    assert MaybeMap(odd_double, pad=-1)(1, 2, 3, 4) == vec_tuple(2, 6, -1, -1)

    pos_square = IfThenElse(__ > 0, __ ** 2, nothing)
    assert MaybeMap(pos_square, pad=0)(-20, 2, -2, 10, 20) == vec_tuple(4, 100, 400, 0, 0)

    @statistic(codim=1, dim=3)
    def repeat3(v):
        if v > 0:
            return (v, v, v)
        return nothing

    assert MaybeMap(repeat3)(1, 4, 10) == vec_tuple(1, 1, 1, 4, 4, 4, 10, 10, 10)
    assert MaybeMap(repeat3)(1, -4, 4, 0, 10) == vec_tuple(1, 1, 1, 4, 4, 4, 10, 10, 10, nothing, nothing, nothing, nothing, nothing, nothing)
    assert MaybeMap(repeat3, pad=None)(1, -4, 4, 0, 10) == vec_tuple(1, 1, 1, 4, 4, 4, 10, 10, 10)

def test_tuple_safe():
    def sc_fn(x):
        return as_quantity(x) + 1

    s1 = tuple_safe(sc_fn, arities=1, strict=False)
    s1s = tuple_safe(sc_fn, arities=1, strict=True)

    assert s1(4) == vec_tuple(5)
    assert s1((4,)) == vec_tuple(5)
    assert s1(-1) == vec_tuple(0)
    assert s1('1/2') == vec_tuple(1.5)
    assert s1(17, 10) == vec_tuple(18)
    assert s1((17, 10)) == vec_tuple(18)
    assert s1((-101, 1, 2, 3, 4, 5)) == vec_tuple(-100)

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

    assert v1(1, 2, 3) == vec_tuple(1, 2, 3, 0)
    assert v1((1, 2, 3)) == vec_tuple(1, 2, 3, 0)
    assert v1((1, 2, 3, 4, 5, 6, 7, 8)) == vec_tuple(1, 2, 3, 0)

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

    assert v2(1, 2, 3) == vec_tuple(1, 2, 3, 0)
    assert v2((1, 2, 3)) == vec_tuple(1, 2, 3, 0)
    assert v2((1, 2, 3, 4, 5, 6, 7, 8)) == vec_tuple(1, 2, 3, 0)

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
    assert v3(1, 2, 3, 4) == vec_tuple(7)
    assert v3(tuple(range(11))) == vec_tuple(54)
    assert v3(10, 90, 80) == vec_tuple(80)

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

def test_stat_combinators():
    k = either(0, 1) ** 4
    assert Kind.equal(k ^ Proj[1, 2] ^ Sum, k ^ (Proj[1, 2] ^ Sum))
    assert is_statistic(Proj[1, 2] ^ Sum)
    assert codim(Proj[1, 2] ^ Sum) == (2, infinity)
    assert dim(Proj[1, 2] ^ Sum) == 1

