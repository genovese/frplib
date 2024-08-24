from __future__ import annotations

import pytest

from decimal import Decimal

from frplib.exceptions import MismatchedDimensionError
from frplib.vec_tuples import VecTuple, vec_tuple, as_vec_tuple, is_vec_tuple


# Note: lots of room for property testing here!

def test_construction():
    "various ways to construct VecTuples"
    assert is_vec_tuple(VecTuple([10]))
    assert vec_tuple() == VecTuple([])
    assert vec_tuple(1, 2, 3) == VecTuple([1, 2, 3])
    assert as_vec_tuple(10) == VecTuple([10])

def test_vec_operations():
    "vector operations"
    assert vec_tuple(1, 2, 3) + vec_tuple(9, 8, 7) == vec_tuple(10, 10, 10)
    assert vec_tuple(10, 10, 10) - vec_tuple(1, 2, 3) == vec_tuple(9, 8, 7)
    assert vec_tuple(1, 2, 3) * vec_tuple(9, 8, 7) == vec_tuple(9, 16, 21)
    assert vec_tuple(60, 32, 12) / vec_tuple(12, 16, 4) == vec_tuple(5.0, 2.0, 3.0)
    assert vec_tuple(60, 32, 12) // vec_tuple(12, 16, 4) == vec_tuple(5, 2, 3)
    assert vec_tuple(60, 32, 12) % vec_tuple(7, 3, 5) == vec_tuple(4, 2, 2)
    assert vec_tuple(2, 3, 5) ** vec_tuple(2, 3, 4) == vec_tuple(4, 27, 625)

    assert vec_tuple(0, 0, 0, 0) < vec_tuple(0, 0, 0, 1)
    assert vec_tuple(0, 0, 0, 0) <= vec_tuple(0, 0, 0, 1)
    assert vec_tuple(0, 0, 0, 0) <= vec_tuple(0, 0, 0, 0)
    assert vec_tuple(0, 0, 0, 0) >= vec_tuple(0, 0, 0, 0)
    assert vec_tuple(0, 1, 0, 0) >= vec_tuple(0, 0, 0, 0)
    assert vec_tuple(0, 1, 0, 0) > vec_tuple(0, 0, 0, 0)
    assert vec_tuple(0, 1, 0, 0) != vec_tuple(0, 0, 0, 0)

    assert vec_tuple(0, 0, 0, 0) == vec_tuple(0, 0, 0, 0)

    assert not (vec_tuple(0, 1, 0, 0) > vec_tuple(0, 0, 1, 0))
    assert not (vec_tuple(0, 1, 0, 0) < vec_tuple(0, 0, 1, 0))
    assert not (vec_tuple(0, 1, 0, 0) >= vec_tuple(0, 0, 1, 0))
    assert not (vec_tuple(0, 1, 0, 0) <= vec_tuple(0, 0, 1, 0))

def test_scalar_extension():
    "scalar extension rules"
    assert vec_tuple(1, 2, 3) + 1 == vec_tuple(2, 3, 4)
    assert 10 + vec_tuple(1, 2, 3) == vec_tuple(11, 12, 13)
    assert vec_tuple(1, 2, 3) - 1 == vec_tuple(0, 1, 2)
    assert 0 - vec_tuple(1, 2, 3) == vec_tuple(-1, -2, -3)
    assert vec_tuple(1, 2, 3) * 2 == vec_tuple(2, 4, 6)
    assert 100 * vec_tuple(1, 2, 3) == vec_tuple(100, 200, 300)
    assert vec_tuple(10, 12, 15) // 2 == vec_tuple(5, 6, 7)
    assert vec_tuple(10, 12, 15) / 2 == vec_tuple(5.0, 6.0, 7.5)
    assert vec_tuple(1, 2, 3) ** 2 == vec_tuple(1, 4, 9)
    assert vec_tuple(1, 2, 3) % 2 == vec_tuple(1, 0, 1)
    assert 60 / vec_tuple(1, 2, 3, 5) == vec_tuple(60.0, 30.0, 20.0, 12.0)
    assert 60 // vec_tuple(1, 2, 3, 5) == vec_tuple(60, 30, 20, 12)
    assert 2 ** vec_tuple(0, 1, 2, 3) == vec_tuple(1, 2, 4, 8)
    assert 60 % vec_tuple(7, 11, 13) == vec_tuple(4, 5, 8)

def test_mismatched_extension():
    "extension rules for non-scalar, mismatched dimensions"
    # Currently based on scalar_extend from vec_tuples.py
    with pytest.raises(MismatchedDimensionError):
        vec_tuple(1, 2, 3) + vec_tuple(1, 2)
    with pytest.raises(MismatchedDimensionError):
        vec_tuple(1, 2, 3) > vec_tuple(1, 2)
