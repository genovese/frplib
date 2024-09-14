"""
Selected examples from lectures and homeworks etc to stress
test and check the library with some authentic use cases.

"""
from __future__ import annotations

import math

from decimal   import Decimal
from typing    import cast

from frplib.exceptions   import StatisticError
from frplib.expectations import E
from frplib.frps         import evolve
from frplib.kinds        import Kind, kind, conditional_kind, clean, constant, either, uniform, weighted_as, without_replacement
from frplib.quantity     import as_quantity
from frplib.statistics   import statistic, Cases, Fork, Id, Sum, Proj
from frplib.utils        import irange, size


def test_example_a():
    "Craps"
    @conditional_kind
    def next_roll(value):
        first_roll, n_rolls, outcome = value
     
        if outcome == -1 or outcome == 1:
            return constant(value)
     
        n = n_rolls + 1
        vs = [(first_roll, n, w) for w in [-1, 0, 1]]
        win = min(first_roll - 1, 13 - first_roll)
        ws = [8, 28 - win, win]

        return weighted_as(vs, weights=ws)

    d6 = uniform(1, 2, ..., 6)
    win1 = Cases({2: -1, 3: -1, 12: -1, 7: 1, 11: 1}, default=0)

    craps_initial_state = Sum(d6 * d6) ^ Fork(Id, 1, win1)

    assert Kind.equal(craps_initial_state,
                      weighted_as((2, 1, -1),
                                  (3, 1, -1),
                                  (4, 1, 0),
                                  (5, 1, 0),
                                  (6, 1, 0),
                                  (7, 1, 1),
                                  (8, 1, 0),
                                  (9, 1, 0),
                                  (10, 1, 0),
                                  (11, 1, 1),
                                  (12, 1, -1), weights=[f'{min(k - 1, 13 - k)}/36' for k in irange(2, 12)]))


    k = next_roll // craps_initial_state
    assert size(k) == 23
    assert math.isclose(k.kernel(7, 1, 1, as_float=False), cast(Decimal, as_quantity('1/6')))
    assert math.isclose(k.kernel(9, 2, -1, as_float=False), Decimal('0.02469135802469135802469135802'))

    state = craps_initial_state
    for _ in range(41):
        state = next_roll // state
    assert E(state ^ (Proj[3] == 0)) < 1e-7
    w = clean(Proj[3](state), 1e-7)

    assert math.isclose(w.kernel(-1), Decimal('0.5514115402579242426793667628'))
    assert math.isclose(w.kernel(1), Decimal('0.4485884597420757573206332372'))
    

def test_example_b():
    "Box Search HW"

    CARLOS = 1
    RHIANNON = -1
    DRAW = 0
     
    boxes = list(irange(1, 15))
    prizes = without_replacement(2, boxes)
    rhiannon_order = list(irange(1, 15))
    carlos_order = [j + (i - 1)*5 for j in irange(1, 5) for i in irange(1, 3)]
     
    @statistic(codim=2, dim=1)
    def winner(prize_locations):
        prize_boxes = set(prize_locations)
        for round in range(len(boxes)):
            carlos_found = carlos_order[round] in prize_boxes
            rhiannon_found = rhiannon_order[round] in prize_boxes
     
            if carlos_found and rhiannon_found:
                return DRAW
            elif carlos_found:
                return CARLOS
            elif rhiannon_found:
                return RHIANNON
        raise StatisticError('No prize found, which should be impossible. '
                             'Check Carlos\'s and Rhiannon\'s orders for completeness.')
     
    winner_kind = winner(prizes)

    assert Kind.equal(winner_kind,
                      weighted_as({
                          -1: Decimal('0.4095238095238095238095238090'),
                          0: Decimal('0.2190476190476190476190476190'),
                          1: Decimal('0.3714285714285714285714285710'),
                      }))
