from __future__ import annotations

from frplib.frps       import evolve
from frplib.kinds      import Kind, kind, constant, either, uniform, weighted_as

from frplib.examples.labyrinth     import (steps, start, moves, n_moves, after_move_n)

def test_labyrinth():
    assert Kind.equal(start, constant(0))
    assert Kind.equal(start >> moves, uniform((0, 1), (0, 3)))
    assert Kind.equal(start >> moves >> moves,
                      uniform((0, 1, 0), (0, 1, 5), (0, 3, 0), (0, 3, 12)))
    assert Kind.equal(start >> moves >> moves >> moves,
                      weighted_as((0, 1, 0, 1), (0, 1, 0, 3),
                                  (0, 1, 5, 1), (0, 1, 5, 2), (0, 1, 5, 4),
                                  (0, 3, 0, 1), (0, 3, 0, 3),
                                  (0, 3, 12, 3), (0, 3, 12, 17),
                                  weights=['1/8', '1/8', '1/12', '1/12', '1/12',
                                           '1/8', '1/8', '1/8', '1/8']
                                  ))

    second_pos_kind = (start >> moves)[2]
    third_pos_kind = (second_pos_kind >> moves)[2]

    assert Kind.equal(second_pos_kind, either(1, 3))
    assert Kind.equal(third_pos_kind, weighted_as(0, 5, 12, weights=['1/2', '1/4', '1/4']))

    assert Kind.equal(second_pos_kind, moves // start)
    assert Kind.equal(second_pos_kind, ((moves >> moves) // start)[1])
    assert Kind.equal(third_pos_kind, ((moves >> moves) // start)[2])

    combined = start >> moves >> moves
    assert Kind.equal( combined[1], start )
    assert Kind.equal( combined[2], second_pos_kind )
    assert Kind.equal( combined[3], third_pos_kind )
    assert Kind.equal(combined[2:], (moves >> moves) // start)

    paths3 = start >> moves >> moves >> moves
    assert Kind.equal(paths3[4], after_move_n(3, start, moves))
    assert Kind.equal(paths3[4], evolve(start, moves, 3))
    assert Kind.equal(paths3, start >> (moves >> moves >> moves))
    assert Kind.equal(paths3, n_moves(start, moves, 3))

    move100_kind = after_move_n(100, start, steps)
    sexp100 = '(<> 0.04385784726548858109844937288 <0> 0.04540770885385537476701476432 <1> 0.04781030933338388817199012735 <2> 0.04065405995694103546817692374 <3> 0.04781030933338388817199012735 <4> 0.07118513822179711996890369419 <5> 0.03484181223366136653848739815 <11> 0.03883807692285524603539861536 <12> 0.01734560416770452234132454134 <13> 0.03550891990555188590501821529 <14> 0.01763392004058894467718616377 <15> 0.05266202525044446981851586392 <16> 0.05266022277439436621418201162 <17> 0.05261848634829084436229182576 <18> 0.03523153248593811860133233989 <19> 0.01748835824174505548794280518 <20> 0.03359338713248078663742214494 <21> 0.02976597425621051666484285050 <22> 0.02872818911173387291673075423 <23> 0.02500003152681968536407302307 <24> 0.01141066047577320897492297824 <25> 0.03627331722577147723061621084 <26> 0.02151075561958365447651426562 <27> 0.03111395116383969280025816311 <28> 0.02007576754948179881062704911 <29> 0.02994718431874360958016319191 <30> 0.009975672405671353309035761734 <31> 0.07105077787786563560658881715 <32>)'
    k100 = kind(sexp100)
    assert Kind.equal(move100_kind, k100)

