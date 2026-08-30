# pylint: disable=too-many-statements, too-many-function-args, line-too-long, invalid-name, missing-function-docstring

from __future__ import annotations

import math
import pytest

from frplib.exceptions import StatisticError
from frplib.numeric    import numeric_ln
from frplib.quantity   import tup
from frplib.statistics import (Sqrt, Log, Log2, Log10, Cos, Tan,
                               Gamma, GammaLn,
                               FromDegrees,
                               Round,
                               ForEach,
                               )


def test_numeric_statistics():
    assert Sqrt(4) == tup(2)

    with pytest.raises(StatisticError):
        Sqrt(-1)

    assert Log2(4) == tup(2)

    with pytest.raises(StatisticError):
        Log2(0)

    with pytest.raises(StatisticError):
        Log10(-2)

    with pytest.raises(StatisticError):
        Log(-4)

    assert math.isclose(float(Cos(FromDegrees(0))[0]), 1.0)
    assert math.isclose(float(Tan(FromDegrees(45))[0]), 1.0)

def test_special_statistics():
    "Builtin statistics and combinators."

    assert Gamma(4) == tup(6)
    assert math.isclose(float(GammaLn(4)[0]), float(numeric_ln(6)))


def test_rounding():
    assert tup(1, 99.2343456, 256.652, 12345.678) ^ ForEach(Round(2))  == tup(1, 99.23, 256.65, 12345.68)
    assert tup(1, 1.2343456, 2.5, 2.11111111111) ^ ForEach(Round(4))   == tup(1, 1.2343, 2.5000, 2.1111)
    assert tup(1, 1.2343456, 2.5, 2.11111111111) ^ ForEach(Round(0))   == tup(1, 1, 3, 2)
    assert tup(1, 99.2343456, 256.452, 12345.678) ^ ForEach(Round(0))  == tup(1, 99, 256, 12346)
    assert tup(1, 99.2343456, 256.652, 12345.678) ^ ForEach(Round(-1)) == tup(0.0, 99.0, 257.0, 12346.0)
    assert tup(1, 99.2343456, 256.652, 12345.678) ^ ForEach(Round(-2)) == tup(0.0, 100.0, 260.0, 12350.0)
    assert tup(1, 99.2343456, 256.652, 12345.678) ^ ForEach(Round(-4)) == tup(0.0, 0.0, 0.0, 12000.0)
