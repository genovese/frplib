from __future__ import annotations

import pytest

from frplib.examples.dirichlet import solve_dirichlet, solve_dirichlet_sparse, lava_room

from frplib.kinds      import Kind, kind, conditional_kind, binary, constant
from frplib.utils      import irange
from frplib.statistics import __

def test_gamblers_ruin():
    @conditional_kind(codim=1, domain=irange(-5, 7))
    def gr(nw):
        if nw == -5 or nw == 7:
            return constant(nw)
        return binary() ^ (nw + 2 * __ - 1)

    f = solve_dirichlet(gr, fixed=[{-5}, {7}], fixed_values=[0, 1])
    fs = solve_dirichlet_sparse(gr, fixed=[{-5}, {7}], fixed_values=[0, 1])

    for nw in irange(-5, 7):
        assert f(nw) == pytest.approx((nw + 5) / 12)
        assert f(nw) == pytest.approx(fs(nw))

def test_lava_room():
    f = solve_dirichlet_sparse(lava_room.cKind, states=lava_room.states,
                               fixed=lava_room.fixed, fixed_values=(0, 1))

    assert f(0, 0) == pytest.approx(0.8178943428510974)

    end_tiles = lava_room.fixed[0].union(lava_room.fixed[1])
    f_time = solve_dirichlet_sparse(lava_room.cKind, alpha=1, states=lava_room.states,
                             fixed=[end_tiles], fixed_values=[0])
    assert f_time(0, 0) == pytest.approx(66.5864958884486)
