from __future__ import annotations

import math

from frplib.calculate    import substitution
from frplib.expectations import E
from frplib.kinds        import Kind, choice, clean, kind, uniform
from frplib.quantity     import tup
from frplib.statistics   import __, All, And, Round, is_true
from frplib.utils        import dim
from frplib.vec_tuples   import as_float

from frplib.examples.d_and_d               import dnd_attribute, dnd_character
from frplib.examples.buckets_and_balls     import which_bucket_g, which_bucket_n
from frplib.examples.dividing_the_pizza    import C_10
from frplib.examples.tournament            import winner, E_winner, E_bottom_half
from frplib.examples.recursive_rover       import run_rover
from frplib.examples.doubled_cards         import D_kind, T_kind
from frplib.examples.disease_testing_redux import disease_given_negative, disease_given_positive

# For now, we mostly just check that these run


def test_d_and_d():
    assert dim(dnd_attribute()) == 1
    assert dim(dnd_character()) == 6

    for _ in range(8):
        X = dnd_character() ^ All(And(__ >= 3, __ <= 18))
        assert is_true(X.value)

def test_buckets_and_balls():
    assert Kind.equal(which_bucket_g, choice(0, 1, 2))
    assert Kind.equal(which_bucket_n, choice(0, 1, '8/9'))

def test_dividing_the_pizza():
    assert Kind.equal(clean(kind(C_10), tolerance=1e-6), uniform(1, 2, 3))

def test_tournament():
    assert math.isclose(as_float(E_winner ^ Round(5)), 3.15184)
    assert math.isclose(as_float(E_bottom_half ^ Round(5)), 0.24562)
    assert math.isclose(as_float(tup(winner.kernel(8)) ^ Round(5)), 0.03674)

def test_recursive_rover():
    assert math.isclose(as_float(E(run_rover(32)) ^ Round(4)), 15)

def test_doubled_cards():
    assert Kind.equal(D_kind, choice(1, 0, 197))
    assert Kind.equal(T_kind, choice(1, 0, 98))

def disease_testing_redux():
    assert math.isclose(as_float(substitution(E(disease_given_positive), d=1 / 1000, n=950 / 1000, p=900 / 1000)),
                        0.01769911504424779)
    assert math.isclose(as_float(substitution(E(disease_given_negative), d=1 / 1000, n=950 / 1000, p=900 / 1000)),
                        0.0001053574250645314)
