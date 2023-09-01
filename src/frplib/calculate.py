from __future__ import annotations

from frplib.kinds      import Kind
from frplib.symbolic   import Symbolic
from frplib.vec_tuples import VecTuple


#
# Kind and FRP based calculations
#

def substitute(quantity, mapping):
    if hasattr(quantity, 'this'):  # Facades
        quantity = getattr(quantity, 'this')

    if isinstance(quantity, Symbolic):
        return quantity.substitute(mapping)

    if isinstance(quantity, VecTuple):
        return quantity.map(substitute_with(mapping))

    if isinstance(quantity, Kind):
        f = substitute_with(mapping)
        return quantity.bimap(f, f)

    if isinstance(quantity, list):
        return [substitute(q, mapping) for q in quantity]

    return quantity

def substitute_with(mapping):
    def sub(quantity):
        return substitute(quantity, mapping)
    return sub
