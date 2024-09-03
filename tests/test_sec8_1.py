from __future__ import annotations

import pytest

from frplib.exceptions  import EvaluationError
from frplib.kinds       import Kind, either
from frplib.statistics  import Sqrt
from frplib.vec_tuples  import vec_tuple
from frplib.utils       import dim, size

from frplib.examples.six_of_one import (vertices, is_equilateral, equilateral,
                                        heron, side_lengths)  

def test_six_of_one():
    assert is_equilateral(1, 3, 5) == vec_tuple(1)
    assert is_equilateral(1, 4, 6) == vec_tuple(0)

    assert dim(vertices) == 3
    assert size(vertices) == 20

    assert Kind.equal(equilateral, either(0, 1, 9))

    assert heron(3, 4, 5) == 6
    assert heron(1, 1, Sqrt(2)) == 0.5

    with pytest.raises(EvaluationError):
        heron(1, 3, 5)  # Not a triangle

    assert side_lengths(1, 3, 5) == (Sqrt(3), Sqrt(3), Sqrt(3))
    assert side_lengths(2, 4, 6) == (Sqrt(3), Sqrt(3), Sqrt(3))
    assert side_lengths(1, 4, 6) == (1, 2, Sqrt(3))
