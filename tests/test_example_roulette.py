from __future__ import annotations

from itertools import chain

from frplib.examples.roulette import roulette, RED_SQUARES

from frplib.kinds      import Kind, kind, weighted_as
from frplib.utils      import irange
from frplib.vec_tuples import vec_tuple

def test_roulette_basics():
    R = roulette()
    kind_R = kind(R)
    assert Kind.equal(roulette.kind, kind_R)
    assert Kind.equal(roulette.even(kind_R),
                      weighted_as(-1, 1, weights=['10/19', '9/19']))
    assert Kind.equal(roulette.straight(16)(kind_R),
                      weighted_as(-1, 35, weights=['37/38', '1/38']))

def test_roulette_plays():
    lost = vec_tuple(-1)
    won = vec_tuple(1)    # scale as needed

    assert all( roulette.even(p) == won for p in irange(2, 36, step=2) )
    assert all( roulette.even(p) == lost for p in irange(-1, 36, step=2) )
    assert roulette.even(0) == lost
    assert all( roulette.odd(p) == won for p in irange(1, 36, step=2) )
    assert all( roulette.odd(p) == lost for p in irange(2, 36, step=2) )
    assert roulette.odd(0) == lost
    assert roulette.odd(-1) == lost

    assert all( roulette.red(p) == won for p in RED_SQUARES )
    assert all( roulette.red(p) == lost for p in irange(-1, 36) if p not in RED_SQUARES )
    assert all( roulette.black(p) == won for p in irange(1, 36) if p not in RED_SQUARES )
    assert all( roulette.black(p) == lost for p in RED_SQUARES )
    assert roulette.black(0) == lost
    assert roulette.black(-1) == lost

    assert all( roulette.first18(p) == won for p in irange(1, 18) )
    assert all( roulette.second18(p) == won for p in irange(19, 36) )
    assert all( roulette.first18(p) == lost for p in irange(-1, 36) if p < 1 or p > 18)
    assert all( roulette.second18(p) == lost for p in irange(-1, 18) )

    assert all( roulette.dozen(1) == 2 * won for p in irange(1, 12) )
    assert all( roulette.dozen(2) == 2 * won for p in irange(13, 24) )
    assert all( roulette.dozen(3) == 2 * won for p in irange(25, 36) )
    assert all( roulette.dozen('first') == 2 * won for p in irange(1, 12) )
    assert all( roulette.dozen('second') == 2 * won for p in irange(13, 24) )
    assert all( roulette.dozen('third') == 2 * won for p in irange(25, 36) )
    assert all( roulette.dozen(1) == lost for p in chain([-1, 0], irange(13, 36)) )
    assert all( roulette.dozen(2) == lost for p in chain(irange(-1, 12), irange(25, 36)) )
    assert all( roulette.dozen(3) == lost for p in irange(-1, 24) )

    assert all( roulette.column(1) == 2 * won for p in irange(1, 36) if p % 3 == 1 )
    assert all( roulette.column(2) == 2 * won for p in irange(1, 36) if p % 3 == 2 )
    assert all( roulette.column(3) == 2 * won for p in irange(1, 36) if p % 3 == 0 )
    assert all( roulette.column(1) == lost    for p in irange(1, 36) if p % 3 != 1 )
    assert all( roulette.column(2) == lost    for p in irange(1, 36) if p % 3 != 2 )
    assert all( roulette.column(3) == lost    for p in irange(1, 36) if p % 3 != 0 )
    assert all( roulette.column(i)(0) == lost  for i in irange(1, 3) )
    assert all( roulette.column(i)(-1) == lost for i in irange(1, 3) )

    assert all( roulette.top_line == 5 * won for p in irange(-1, 3) )
    assert all( roulette.top_line == lost for p in irange(4, 36) )

    assert all( roulette.six_line(3 * u + k)(3 * u + p) == 5 * won
                for u in range(11) for k in irange(1, 3) for p in irange(1, 6) )
    assert all( roulette.six_line(p)(-1) == lost for p in irange(1, 36) )
    assert all( roulette.six_line(p)(0) == lost for p in irange(1, 36) )
    assert all( roulette.six_line(3 * u + k)(p) == lost
                for u in range(11) for k in irange(1, 3) for p in irange(1, 3 * u) )
    assert all( roulette.six_line(3 * u + k)(p) == lost
                for u in range(11) for k in irange(1, 3) for p in irange(3 * u + 7, 36) )

    assert all( roulette.street(3 * u + k)(3 * u + p) == 11 * won
                for u in range(11) for k in irange(1, 3) for p in irange(1, 3) )
    assert all( roulette.street(p)(-1) == lost for p in irange(1, 36) )
    assert all( roulette.street(p)(0) == lost for p in irange(1, 36) )
    assert all( roulette.street(3 * u + k)(p) == lost
                for u in range(11) for k in irange(1, 3) for p in irange(1, 3 * u) )
    assert all( roulette.street(3 * u + k)(p) == lost
                for u in range(11) for k in irange(1, 3) for p in irange(3 * u + 4, 36) )

    assert all( roulette.corner(3 * u + k)(x) == 8 * won for u in range(11) for k in [1, 2]
                for x in [3 * u + k, 3 * u + k + 1, 3 * u + k + 3, 3 * u + k + 4] )
    assert all( roulette.corner(3 * u + k)(x) == lost for u in range(11) for k in [1, 2]
                for x in irange(-1, 36, exclude={3 * u + k, 3 * u + k + 1, 3 * u + k + 3, 3 * u + k + 4}) )

    assert all( roulette.split(3 * u + k, p)(3 * u + k) == 17 * won
                for u in range(11) for k in irange(1, 2) for p in [3 * u + k + 1, 3 * u + k + 3] )
    assert all( roulette.split(3 * u + k, p)(p) == 17 * won
                for u in range(11) for k in irange(1, 2) for p in [3 * u + k + 1, 3 * u + k + 3] )
    assert all( roulette.split(3 * u, 3 * u + 1)(p) == 17 * won
                for u in irange(1, 11) for p in [3 * u, 3 * u + 1])
    assert all( roulette.split(u, u + 1)(p) == 17 * won
                for u in irange(34, 35) for p in [u, u + 1] )
    assert all( roulette.split(3 * u + k, p)(3 * u + k) == 17 * won
                for u in range(11) for k in irange(1, 2) for p in [3 * u + k + 1, 3 * u + k + 3] )
    assert all( roulette.split(3 * u + k, p)(x) == lost
                for u in range(11) for k in irange(1, 2) for p in [3 * u + k + 1, 3 * u + k + 3]
                for x in irange(-1, 36, exclude={3 * u + k, 3 * u + k + 1, 3 * u + k + 3}) )
    assert all( roulette.split(3 * u, 3 * u + 1)(x) == lost
                for u in irange(1, 11) for p in [3 * u, 3 * u + 1]
                for x in irange(-1, 36, exclude={3 * u, 3 * u + 1}) )
    assert all( roulette.split(u, u + 1)(p) == lost
                for u in irange(34, 35) for p in irange(-1, 36, exclude={u, u + 1}) )

    assert all( roulette.straight(p)(p) == 35 * won for p in irange(-1, 36) )
    assert all( roulette.straight(p)(q) == lost for p in irange(-1, 36) for q in irange(-1, 36) if p != q )

def test_text():
    R = roulette()
    s16_10 = 10 * roulette.straight(16)
    W16_10 = R ^ s16_10
    assert Kind.equal(kind(W16_10), weighted_as(-10, 350, weights=['37/38', '1/38']))

    comb = 10 * roulette.even + 5 * roulette.corner(25) + 20 * roulette.straight(4) + 50 * roulette.column(2)
    assert comb(26)[0] == 130

    k = weighted_as(-85, -65, -40, -20, 65, 85, 110, 130, 655,
                    weights=['13/38', '10/38', '1/38', '1/38', '5/38', '5/38', '1/38', '1/38', '1/38'])
    assert Kind.equal(kind(comb(R)), k)
