from __future__ import annotations

from decimal import Decimal

from frplib.kinds      import Kind, kind, weighted_as
from frplib.symbolic   import symbols
from frplib.statistics import IfThenElse, Norm, Proj
from frplib.utils      import irange, lmap
from frplib.vec_tuples import vec_tuple

from frplib.examples.monty_hall    import switch_win, dont_switch_win, outcome_by_strategy
from frplib.examples.circle_points import circle_points

def test_monty_hall():
    assert Kind.equal(dont_switch_win, weighted_as(0, 1, weights=['2/3', '1/3']))
    assert Kind.equal(switch_win, weighted_as(0, 1, weights=['1/3', '2/3']))

    a, b = symbols('a b')
    K0 = outcome_by_strategy(left=a, middle=b, right=1 - a - b)
    K1 = weighted_as([vec_tuple(i, j) for i in irange(3) for j in irange(3)],
                     weights=[a/3, b/3, (1 - a - b)/3, a/3, b/3, (1 - a - b)/3, a/3, b/3, (1 - a - b)/3])
    assert Kind.equal(K0, K1)

def test_circle_points():
    XY = circle_points()

    norm_vals = lmap(vec_tuple,
                     [Decimal('0'), Decimal('1'), Decimal('1.414213562373095048801688724'), Decimal('2'),
                      Decimal('2.236067977499789696409173669'), Decimal('2.828427124746190097603377448'),
                      Decimal('3'), Decimal('3.162277660168379331998893544'), Decimal('3.605551275463989293119221267'),
                      Decimal('4'), Decimal('4.123105625617660549821409856'),
                      Decimal('4.242640687119285146405066173'), Decimal('4.472135954999579392818347337'),
                      Decimal('5')])
    k = weighted_as(norm_vals,
                    weights=[0.012346, 0.049383, 0.049383, 0.049383, 0.098765, 0.049383, 0.049383,
                             0.098765, 0.098765, 0.049383, 0.098765, 0.049383, 0.098765, 0.14815])
    assert Kind.equal(kind(Norm(XY)), k, tolerance=1e-5)

    compareXY = IfThenElse(Proj[1] > Proj[2], 1, IfThenElse(Proj[1] < Proj[2], -1, 0))
    assert Kind.equal(kind(compareXY(XY)),
                      weighted_as(-1, 0, 1, weights=[0.45679, 0.086420, 0.45679]),
                      tolerance=1e-6)
