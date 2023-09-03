from __future__ import annotations

from decimal import Decimal

from frplib.kinds      import sequence_of_values, Flatten
from frplib.numeric    import as_numeric
from frplib.symbolic   import symbol, is_symbolic
from frplib.utils      import every, lmap
from frplib.vec_tuples import as_vec_tuple, vec_tuple


#
# Helpers
#

def numeric(x):
    return x if x is Ellipsis else as_numeric(x)

def test_simple_seq():
    "Simple sequence patterns."
    assert (sequence_of_values(1, 2, ..., 8) ==
            [1, 2, 3, 4, 5, 6, 7, 8])
    assert (sequence_of_values((1, 2), (3, 4), (5, 6), (7, 8)) ==
            [1, 2, 3, 4, 5, 6, 7, 8])
    assert (sequence_of_values(1, 2, ..., 10, 12, ..., 22) ==
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22])
    assert (sequence_of_values((1, 2), (3, 4), (5, 6), (7, 8),
                               pre_transform=as_vec_tuple) ==
            [vec_tuple(1, 2), vec_tuple(3, 4), vec_tuple(5, 6), vec_tuple(7, 8)])
    assert (sequence_of_values((1, 2), (3, 4), (5, 6), (7, 8),
                               flatten=Flatten.EVERYTHING, pre_transform=as_vec_tuple) ==
            [1, 2, 3, 4, 5, 6, 7, 8])
    assert (sequence_of_values('1.2', '2.4', ..., '10',
                               pre_transform=numeric) ==
            [Decimal('1.2'), Decimal('2.4'), Decimal('3.6'), Decimal('4.8'),
             Decimal('6.0'), Decimal('7.2'), Decimal('8.4'), 10])

def test_symbol_seq():
    a = symbol('a')
    b = symbol('b')
    assert every(is_symbolic, sequence_of_values(a, b, 2 * a))
    assert lmap(str, sequence_of_values(a, b, 2 * a)) == ['a', 'b', '2 a']
