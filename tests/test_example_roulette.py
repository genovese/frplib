from __future__ import annotations

from itertools import chain

from frplib.examples.roulette import roulette, RED_SQUARES

from frplib.kinds      import Kind, kind
from frplib.utils      import irange
from frplib.vec_tuples import vec_tuple

def test_roulette_basics():
    assert Kind.equal(roulette.kind, kind(roulette()))

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

    assert all( roulette.six_line(p)(-1) == lost for p in irange(1, 36) )
    assert all( roulette.six_line(p)(0) == lost for p in irange(1, 36) )

    # ATTN: finish six_line, corner, street, and split

    assert all( roulette.straight(p)(p) == 35 * won for p in irange(-1, 36) )
    assert all( roulette.straight(p)(q) == lost for p in irange(-1, 36) for q in irange(-1, 36) if p != q )
