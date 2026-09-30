from __future__ import annotations

import math
import pytest

from hypothesis             import given
from hypothesis.strategies  import (SearchStrategy, decimals, floats, fractions,
                                    integers, lists, one_of, sampled_from)

from frplib.numeric    import Nothing, nothing
from frplib.quantity   import tup
from frplib.symbolic   import Symbolic, symbol
from frplib.vec_tuples import VecTuple

numerics = one_of(
    integers(),
    fractions(max_denominator=10**6),
    floats(allow_nan=False, allow_infinity=False),
    decimals(allow_nan=False, allow_infinity=False, places=6, min_value=-10**12, max_value=10**12),
)
symbols = sampled_from('abc')   # tup converts strings to symbols

def quant_vecs(elements: SearchStrategy = numerics, min_dim: int = 1, max_dim: int = 6) -> SearchStrategy[VecTuple]:
    "Strategy for quantity VecTuples, with components converted by `tup`."
    return lists(elements, min_size=min_dim, max_size=max_dim).map(lambda xs: tup(*xs))

numeric_qvecs = quant_vecs()
mixed_qvecs = quant_vecs(one_of(numerics, symbols))

def vec_isclose(u, v, *, rel_tol=1e-9, abs_tol=0.0) -> bool:
    "Componentwise approximate equality; symbolic components must be equal exactly."
    if len(u) != len(v):
        return False
    for x, y in zip(u, v):
        if isinstance(x, (Symbolic, Nothing)) or isinstance(y, (Symbolic, Nothing)):
            if not x == y:
                return False
        elif not math.isclose(x, y, rel_tol=rel_tol, abs_tol=abs_tol):
            return False
    return True

def test_qvec_ops():
    x1 = tup(-1, 2.5, '-1/3', symbol('a'), nothing)

    assert +x1 == x1
    assert -x1 == tup(1, -2.5, '1/3', -symbol('a'), nothing)
    assert vec_isclose(2 * x1, tup(-2, 5, '-2/3', 2 * symbol('a'), nothing))

@given(mixed_qvecs)
def test_neg_involution(v):
    assert -(-v) == v

@given(mixed_qvecs)
def test_zero_ops(v):
    assert 0 * v == tup(0 if vi is not nothing else nothing for vi in v)
    assert v * 0 == tup(0 if vi is not nothing else nothing for vi in v)
    assert v - v == tup(0 if vi is not nothing else nothing for vi in v)

@given(mixed_qvecs)
def test_pos_identity(v):
    assert +v == v

@given(mixed_qvecs)
def test_double(v):
    assert 2 * v == v * 2
    assert v + v == 2 * v

@given(numeric_qvecs)
def test_div_mul_roundtrip(v):
    assert vec_isclose((v / 3) * 3, v)
