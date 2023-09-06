from __future__ import annotations

import pytest

from frplib.exceptions import KindError
from frplib.kinds      import (kind, conditional_kind,
                               constant, either, uniform,
                               symmetric, linear, geometric,
                               weighted_by, weighted_as, arbitrary,
                               integers, evenly_spaced, bin,
                               subsets, permutations_of,
                               )
from frplib.quantity   import as_quantity
from frplib.statistics import Proj
from frplib.symbolic   import symbol
from frplib.utils      import lmap
from frplib.vec_tuples import vec_tuple


def values_of(u):
    return u.keys()

def weights_of(u):
    return list(u.values())


def test_kinds_factories():
    "Builtin kind factories"
    a = symbol('a')

    assert constant(1).values == {1}
    assert constant((2,)).values == {2}
    assert constant((2, 3)).values == {vec_tuple(2, 3)}

    assert either(0, 1).values == {0, 1}
    assert weights_of(either(0, 1, 2).weights) == pytest.approx([as_quantity('2/3'), as_quantity('1/3')])
    assert lmap(str, values_of(either(a, 2 * a, 2).weights)) == ['<a>', '<2 a>']

    u = uniform(1, 2, 3).weights
    assert values_of(u) == {vec_tuple(1), vec_tuple(2), vec_tuple(3)}
    assert weights_of(u) == pytest.approx([as_quantity('1/3'), as_quantity('1/3'), as_quantity('1/3')])

    w = weighted_as(1, 2, 3, weights=[1, 2, 4]).weights
    assert values_of(w) == {vec_tuple(1), vec_tuple(2), vec_tuple(3)}
    assert weights_of(w) == pytest.approx([as_quantity('1/7'), as_quantity('2/7'), as_quantity('4/7')])

    w = weighted_as(1, 2, 3, weights=[a, 2 * a, 4 * a]).weights
    assert values_of(w) == {vec_tuple(1), vec_tuple(2), vec_tuple(3)}
    assert weights_of(w) == pytest.approx([as_quantity('1/7'), as_quantity('2/7'), as_quantity('4/7')])

    w = weighted_as(1, 2, 3, weights=[1, 2 * a, 4 * a]).weights
    assert values_of(w) == {vec_tuple(1), vec_tuple(2), vec_tuple(3)}
    assert lmap(str, weights_of(w)) == ['1/(1 + 6 a)', '2 a/(1 + 6 a)', '4 a/(1 + 6 a)']

    w = weighted_as(a, 2 * a, 3 * a, weights=[1, 2, 4]).weights
    assert lmap(str, values_of(w)) == ['<a>', '<2 a>', '<3 a>']
    assert weights_of(w) == pytest.approx([as_quantity('1/7'), as_quantity('2/7'), as_quantity('4/7')])

def test_mixtures():
    k0 = either(10, 20)
    m0 = {10: either(4, 8, 99), 20: either(8, 4, 99)}
    m1 = conditional_kind(m0)
    me1 = {10: either(4, 8, 99), 30: either(8, 4, 99)}
    me2 = {10: either(4, 8, 99), (20, 30): either(8, 4, 99)}
    mec1 = conditional_kind(me1)
    mec2 = conditional_kind(me2)

    mix = (k0 >> m1).weights
    assert weights_of(mix) == pytest.approx([as_quantity('0.495'),
                                             as_quantity('0.005'),
                                             as_quantity('0.005'),
                                             as_quantity('0.495')])

    assert values_of(mix) == {vec_tuple(10, 4),
                              vec_tuple(10, 8),
                              vec_tuple(20, 4),
                              vec_tuple(20, 8),
                              }

    mix = (k0 >> m0).weights
    assert weights_of(mix) == pytest.approx([as_quantity('0.495'),
                                             as_quantity('0.005'),
                                             as_quantity('0.005'),
                                             as_quantity('0.495')])

    assert values_of(mix) == {vec_tuple(10, 4),
                              vec_tuple(10, 8),
                              vec_tuple(20, 4),
                              vec_tuple(20, 8),
                              }

    with pytest.raises(KindError):
        k0 >> me1

    with pytest.raises(KindError):
        k0 >> me2

    with pytest.raises(KindError):
        k0 >> mec1

    with pytest.raises(KindError):
        k0 >> mec2

    k1 = k0 >> m1 | (Proj[2] == 8)
    assert weights_of(k1.weights) == pytest.approx([as_quantity('0.01'), as_quantity('0.99')])
    assert values_of(k1.weights) == {vec_tuple(10, 8), vec_tuple(20, 8)}

    has_disease = either(0, 1, 999)     # No disease has higher weight
    test_by_status = conditional_kind({
        vec_tuple(0): either(0, 1, 99),     # No disease, negative has high weight
        vec_tuple(1): either(0, 1, '1/19')  # Yes disease, positive higher weight
    })

    dStatus_and_tResult = has_disease >> test_by_status
    Disease_Status = Proj[1]
    Test_Result = Proj[2]

    has_disease_updated = (dStatus_and_tResult | (Test_Result == 1))[Disease_Status]

    w = dStatus_and_tResult.weights
    assert values_of(w) == { vec_tuple(0, 0), vec_tuple(0, 1), vec_tuple(1, 0), vec_tuple(1, 1) }
    assert weights_of(w) == pytest.approx([as_quantity(v)
                                           for v in ['98901/100000', '999/100000', '1/20000', '19/20000']])

    w = has_disease_updated.weights
    assert values_of(w) == { vec_tuple(0), vec_tuple(1) }
    assert weights_of(w) == pytest.approx([as_quantity(v) for v in ['999/1094', '95/1094']])
