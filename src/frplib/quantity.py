from __future__ import annotations

import re

from collections.abc   import Iterable

from frplib.numeric    import Numeric, ScalarQ, as_numeric, as_real, numeric_q_from_str
from frplib.symbolic   import Symbolic, symbol
from frplib.vec_tuples import VecTuple, vec_tuple

def as_quantity(
        x: ScalarQ | Symbolic = 0,
        convert_numeric=as_numeric
) -> Numeric | Symbolic:
    if isinstance(x, Symbolic):
        return x

    if isinstance(x, str):
        if re.match(r'\s*[-+.0-9]', x):
            return convert_numeric(numeric_q_from_str(x))
        return symbol(x)

    return convert_numeric(x)

def as_real_quantity(x: ScalarQ | Symbolic) -> Numeric | Symbolic:
    return as_quantity(x, convert_numeric=as_real)

def as_quant_vec(x, convert=as_quantity):
    # ATTN: Consider using as_real here
    if isinstance(x, Iterable) and not isinstance(x, str):
        return VecTuple(map(convert, x))
    else:
        return vec_tuple(convert(x))
