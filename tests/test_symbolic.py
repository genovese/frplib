from __future__ import annotations

from frplib.symbolic  import symbol, gen_symbol

#
# Helpers
#

def test_symbol_arithmetic():
    "Simple sequence patterns."
    a = symbol('a')
    b = symbol('b')
    c = symbol('c')

    assert str(a) == 'a'
    assert str(b) == 'b'
    assert str(a - a) == '0'
    assert str(1 + a) == '1 + a'
    assert str((1 + a) * (1 - a)) == '1 + -1 a^2'
    assert str(1 + b + b**2 + b**3) == '1 + b + b^2 + b^3'
    assert str((a - a) * (1 + b + b**2 + b**3)) == '0'

    assert str(1.2 * a) == '1.2 a'
    assert str((1.2 * a) ** 2) == '1.44 a^2'

    assert str(gen_symbol()) != str(gen_symbol())

    assert str(1 / (1 + a)) == '1/(1 + a)'
    assert str((1 + a) / a) == '(1 + a)/a'
    assert str((1 + a) / a**2) == '(1 + a)/a^2'
    assert str((1 + a) / (2 * a**2)) == '(1 + a)/(2 a^2)'

    assert str(((1 + a) * (1 - a) * (1 + a**2)) / (1 - a**4)) == '1'
    assert str(a / (1 - a)) == 'a/(1 + -1 a)'
    assert str(1 + a / (1 - a)) == '1/(1 + -1 a)'

    s = a + b + c
    assert str(s) == 'a + b + c'
    assert str(a / s) == 'a/(a + b + c)'
    assert str(a / s + b / s + c / s) == '1'
    assert str(0.5 * a / s) == '0.5 a/(a + b + c)'


def test_symbol_simplifier():
    "Simple simplifications."
    a = symbol('a')

    assert str(1 + a - a) == '1'
    assert str(1 + a - 1) == 'a'
    assert str((1 + a + a**2) * (1 + a - a - 1)) == '0'
    assert str(((1 + a) * (1 - a) * (1 + a**2)) / (1 - a**4)) == '1'
    assert str(a / (1 + a) + a**2 / (a * (1 + a)) + 2 / (1 + a)) == '2'

    p = a / (1 - a)
    q = 1 / (1 - a)
    assert str(1 / (1 + p)) == '1 + -1 a'
    assert str(a * q) == 'a/(1 + -1 a)'

    assert str((1 / (1 + a)) + (a / (1 + a))) == '1'
    assert str((2 * a / (1 + a) + 2 / (1 + a))) == '2'
    assert str((2 * a / (1 - a) - 2 / (1 - a))) == '-2'

    x = a * (1 + a)
    assert str(x / a) == '1 + a'
    assert str(x / (1 + a)) == 'a'
    assert str((a + a * a) / (1 + a)) == 'a'
    assert str((a + a * a + a**3) / a) == '1 + a + a^2'
