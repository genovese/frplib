from __future__ import annotations

import math

import pytest

from frplib.statistics import (Statistic, Condition, MonoidalStatistic,
                               is_statistic, statistic, condition, scalar_statistic,
                               tuple_safe, infinity,
                               fork, chain, compose,
                               Id, Scalar, __, Proj, _x_,
                               Sum, Count, Max, Min, Mean, Abs,
                               Sqrt, Floor, Ceil,
                               Exp, Log, Log2, Log10,
                               Sin, Cos, Tan, ATan2, Sinh, Cosh, Tanh,
                               Diff, Diffs, Permute,
                               Constantly, Fork, ForEach, IfThenElse,
                               And, Or, Not, Xor, top, bottom,
                               )
from frplib.quantity   import as_quantity
from frplib.symbolic   import symbol
from frplib.vec_tuples import vec_tuple


def test_builtin_statistics():
    "Builtin statistics and combinators."

    assert (2 * __)(1) == vec_tuple(2)
    assert (2 * __)((1,)) == vec_tuple(2)
    assert (2 * __)((1, 2, 3)) == vec_tuple(2, 4, 6)

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

    assert Sqrt(4) == vec_tuple(2)
    assert Sqrt(1.44) == vec_tuple(as_quantity(1.2))
