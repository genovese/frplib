from __future__ import annotations

from frplib.parsing.kind_strings import validate_kind, kind_sexp

def is_valid(sexp: str) -> bool:
    try:
        k = kind_sexp.parse(sexp)
        return validate_kind(k) == ''
    except Exception:
        return False

def test_validate_sexps():
    "Kind validation from sexp string input"

    assert is_valid('(<> 1 (<1> 1 <1, 2> 2 <1, 4> 4 <1, 8>) 9 (<3> 0.2 <3, 2> 0.4 <3, 7> 0.1 <3, 21>))')
    assert is_valid('(<> 1 <2>)')
    assert is_valid('(<> 1/7 (<2> 1 <2, 3> 1 <2, 4>) 1 (<5> 2 <5, 5> 3 <5, 10>))')
    assert is_valid('(<> 1/7 (<2> 1 <2, 3> 1 <2, 4_000_000>) 1 (<5> 2 <5, 52.0e-5> 3 <5, 10.2>))')

    assert is_valid('(<> 1 (<2> 1 <2,3>) 2 (<3> 1 <3,4>))')
    assert is_valid('(<> 1 (<2> 1 <2, 3>) 2 (<3> 1 <3, 4/7>))')
    assert is_valid('(<> 1 (<1> 1 <1, 2> 2 <1, 4> 4 <1, 8>) 9 (<3> 0.2 <3, 2> 0.4 <3, 7> 0.1 <3, 21>))')
    assert is_valid('(<> 1 <2> 2 <2e10>)')
    assert is_valid('(<> 1/7 (<2> 1 <2, 3> 1 <2, 4_000_000>) 1 (<5> 2 <5, 52.0e-5> 3 <5, 10.2>))')
    assert is_valid('(<> 1 (<2> 1 <2, 3> 1 <2, 4>) 1 (<5> 2 <5, 5> 3 <5, 10>))')
    assert is_valid('(<> 1 <2> 3 <4>)')
    assert is_valid('(<> 1 <2> 2 <3>)')

    # Should we allow this? Maybe not
    # assert is_valid('(<> 1 <2, 3> 2 <2, 4>)')
    # assert is_valid('(<> 1 <2, 3, 5> 2 <2, 4, 1> 3 <3, 1, 1>)')

    assert not is_valid('(<> 1 (<0> 1 <0, 0> 2 <0, 1> 3 <0, 2>) 2 <1>)')
    assert not is_valid('(<> 1 <2> 3 <2>)')
    assert not is_valid('(<> 1 <2> 3 <1, 2>)')
    assert not is_valid('(<> 1 <1> 0 <2>)')
    assert not is_valid('(<> 1 <1> 3 (<2> 1 <3, 2> 1 <2, 4>))')
    assert not is_valid('(<> 1 <1> 3 (<2> 1 <2, 2> 1 <2, 4> 2.2 <2, 5, 1>))')
    assert not is_valid('(<> 1 <1> 3 (<2> 0.2 <2, 2> 0 <2, 4> 2.2 <2, 5>))')
