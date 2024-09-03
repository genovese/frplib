from __future__ import annotations

import math
import pytest

from frplib.exceptions import DomainDimensionError, InputError
from frplib.kinds      import Kind, either
from frplib.statistics import (Statistic, Condition, MonoidalStatistic,
                               is_statistic, statistic, condition, scalar_statistic,
                               tuple_safe, infinity, ANY_TUPLE,
                               fork, chain, compose,
                               Id, Scalar, __, Proj, _x_,
                               Sum, Count, Product, Max, Min, Mean, Abs,
                               Sqrt, Floor, Ceil,
                               Exp, Log, Log2, Log10,
                               Sin, Cos, Tan, ATan2, Sinh, Cosh, Tanh,
                               FromDegrees,
                               Diff, Diffs, Permute,
                               SumSq, Norm, Dot, Ascending, Descending,
                               Constantly, Fork, ForEach, IfThenElse,
                               And, Or, Not, Xor, top, bottom,
                               )
from frplib.quantity   import as_quantity, qvec
from frplib.symbolic   import symbol
from frplib.utils      import codim, dim
from frplib.vec_tuples import vec_tuple


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
    

def test_tuple_safe():
    def sc_fn(x):
        return as_quantity(x) + 1   # type: ignore

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

