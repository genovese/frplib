from __future__ import annotations

from frplib.kinds      import Kind, weighted_as
from frplib.symbolic   import symbols
from frplib.utils      import irange
from frplib.vec_tuples import vec_tuple

from frplib.examples.monty_hall import switch_win, dont_switch_win, outcome_by_strategy


def test_monty_hall():
    assert Kind.equal(dont_switch_win, weighted_as(0, 1, weights=['2/3', '1/3']))
    assert Kind.equal(switch_win, weighted_as(0, 1, weights=['1/3', '2/3']))

    a, b = symbols('a b')
    K0 = outcome_by_strategy(left=a, middle=b, right=1 - a - b)
    K1 = weighted_as([vec_tuple(i, j) for i in irange(3) for j in irange(3)],
                     weights=[a/3, (1 - a - b)/3, b/3, a/3, (1 - a - b)/3, b/3, a/3, (1 - a - b)/3, b/3])
    assert Kind.equal(K0, K1)
