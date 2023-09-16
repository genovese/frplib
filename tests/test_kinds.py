from __future__ import annotations

import pytest

from frplib.exceptions import KindError
from frplib.kinds      import (Kind, kind, conditional_kind,
                               constant, either, uniform,
                               symmetric, linear, geometric,
                               weighted_by, weighted_as, arbitrary,
                               integers, evenly_spaced, bin,
                               subsets, permutations_of,
                               fast_mixture_pow)
from frplib.numeric    import as_numeric, numeric_log2
from frplib.quantity   import as_quantity
from frplib.statistics import Proj, Sum, Min, Max
from frplib.symbolic   import symbol
from frplib.utils      import irange, lmap
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
    assert values_of(w) == {vec_tuple(0, 0), vec_tuple(0, 1), vec_tuple(1, 0), vec_tuple(1, 1)}
    assert weights_of(w) == pytest.approx([as_quantity(v)
                                           for v in ['98901/100000', '999/100000', '1/20000', '19/20000']])

    w = has_disease_updated.weights
    assert values_of(w) == { vec_tuple(0), vec_tuple(1) }
    assert weights_of(w) == pytest.approx([as_quantity(v) for v in ['999/1094', '95/1094']])

def test_tagged_kinds():
    k = either(0, 1) * either(2, 3) * either(4, 5)

    k1 = Sum @ k | (Proj[2] == 2)

    list(k1.weights.values()) == [as_quantity('1/4'), as_quantity('1/2'), as_quantity('1/4')]
    list(k1.weights.keys()) == [vec_tuple(6), vec_tuple(7), vec_tuple(8)]

    k2 = Min @ k | (Proj[2] == 2)

    list(k2.weights.values()) == [as_quantity('1/4'), as_quantity('1/2'), as_quantity('1/4')]
    list(k2.weights.keys()) == [vec_tuple(6), vec_tuple(8), vec_tuple(9)]

def test_comparisons():
    assert 'same' in Kind.compare(uniform(1, 2), either(1, 2))
    assert 'differ' in Kind.compare(uniform(1, 2), either(1, 3))
    assert 'differ' in Kind.compare(uniform(1, 2), weighted_as(1, 2, weights=[0.999, 1.001]))

    assert Kind.equal(uniform(1, 2), either(1, 2))
    assert not Kind.equal(uniform(1, 2), either(1, 3))
    assert not Kind.equal(uniform(1, 2), weighted_as(1, 2, weights=[0.999, 1.001]))

    assert Kind.divergence(uniform(0, 2), uniform(0, 2)) == 0
    assert Kind.divergence(uniform(0, 2), weighted_as(1, 2, weights=[0.999, 1.001])) == as_quantity('Infinity')
    assert Kind.divergence(uniform(1, 2), weighted_as(1, 2, weights=['1/4', '3/4'])) == \
        pytest.approx(as_numeric('1/2') - numeric_log2('1.5') / 2)   # type: ignore

def test_fast_pow():
    assert Kind.equal(fast_mixture_pow(Sum, either(0, 1), 0), constant(0))
    assert Kind.equal(fast_mixture_pow(Min, either(0, 1), 0), constant('infinity'))
    assert Kind.equal(fast_mixture_pow(Max, either(0, 1), 0), constant('-infinity'))
    assert Kind.equal(fast_mixture_pow(Sum, either(0, 1), 1), either(0, 1))
    assert Kind.equal(fast_mixture_pow(Sum, either(0, 1), 2), Sum(either(0, 1) * either(0, 1)))
    assert Kind.equal(fast_mixture_pow(Sum, either(0, 1), 5), Sum(either(0, 1) ** 5))

def test_factory_details():
    # Test for roundoff that was happening in the differences with ...
    a_values = [as_numeric(0.05) * k for k in irange(1, 19)]
    k = uniform(0.05, 0.1, ..., 0.95)
    assert Kind.equal(k, uniform(a_values), tolerance='1.0e-16')

    k1 = weighted_as({0.05: 1, 0.45: 2, 0.70: 3})
    k2 = weighted_as(0.05, 0.45, 0.70, weights=[1, 2, 3])
    assert Kind.equal(k1, k2, tolerance='1.0e-16')

def test_indexing():
    k = either(0, 1) * either(2, 3) * either(4, 5) * either(6, 7)
    assert Kind.equal(k[:2], either(0, 1))
    assert Kind.equal(k[:-1], either(0, 1) * either(2, 3) * either(4, 5))
    assert Kind.equal(k[-3:-1], either(2, 3) * either(4, 5))
    with pytest.raises(KindError):
        k[5]
    with pytest.raises(KindError):
        k[-5]
    assert Kind.equal(k[:1], Kind.empty)
