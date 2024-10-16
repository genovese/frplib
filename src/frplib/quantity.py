from __future__ import annotations

import re

from collections.abc   import Iterable
from decimal           import Decimal
from fractions         import Fraction
from itertools         import zip_longest
from typing            import Callable, overload

from frplib.numeric    import (NICE_DIGITS, Numeric, NumericQ, ScalarQ, nothing, Nothing,
                               as_nice_numeric, as_numeric, as_real,
                               numeric_q_from_str, show_values, show_nice_numeric)
from frplib.symbolic   import Symbolic, symbol
from frplib.vec_tuples import VecTuple, vec_tuple


INFINITY = numeric_q_from_str('Infinity').value
NEGATIVE_INFINITY = numeric_q_from_str('-Infinity').value

@overload
def as_quantity(
        x: int | float | Fraction | Decimal | NumericQ = 0,
        convert_numeric: Callable[[NumericQ], Numeric] = as_numeric
) -> Numeric:
    ...

@overload
def as_quantity(
        x: Symbolic, 
        convert_numeric: Callable[[NumericQ], Numeric] = as_numeric
) -> Symbolic:
    ...

@overload
def as_quantity(
        x: Nothing,
        convert_numeric: Callable[[NumericQ], Numeric] = as_numeric
) -> Nothing:
    ...

@overload
def as_quantity(
        x: str,
        convert_numeric: Callable[[NumericQ], Numeric] = as_numeric
) -> Numeric | Symbolic | Nothing:
    ...

def as_quantity(
        x = 0,
        convert_numeric = as_numeric  # as_nice_numeric  # ATTN: as_numeric instead??
):
    if isinstance(x, Symbolic):
        return x

    if isinstance(x, str):
        if re.match(r'\s*[-+.0-9]', x) or re.match(r'(?i)-?inf(?:inity)?', x):
            return convert_numeric(numeric_q_from_str(x))
        elif x.lower() == 'nothing':
            return nothing
        return symbol(x)

    if isinstance(x, Nothing):
        return nothing

    return convert_numeric(x)

@overload
def as_real_quantity(x: int | float | Fraction | Decimal | NumericQ) -> Numeric:
    ...

@overload
def as_real_quantity(x: Symbolic) -> Symbolic:
    ...

@overload
def as_real_quantity(x: Nothing) -> Nothing:
    ...

@overload
def as_real_quantity(x: str) -> Numeric | Symbolic | Nothing:
    ...

def as_real_quantity(x):
    return as_quantity(x, convert_numeric=as_real)

def as_nice_quantity(x: ScalarQ | Symbolic) -> Numeric | Symbolic | Nothing:
    return as_quantity(x, convert_numeric=as_nice_numeric)

def as_quant_vec(x, convert=as_quantity):
    "Converts an iterable or a value into a vector-style tuple with numerics or symbols."
    # ATTN: Consider using as_real for the convert_numeric in as_quantity
    if isinstance(x, Iterable) and not isinstance(x, str):
        return VecTuple(map(convert, x))
    else:
        return vec_tuple(convert(x))

def qvec(*xs, convert=as_quantity):
    "Wraps its arguments in a quantitative vector. If given a single iterable, converts that instead."
    if len(xs) == 0:
        return vec_tuple()
    if len(xs) == 1 and isinstance(xs[0], Iterable) and not isinstance(xs[0], str):
        return as_quant_vec(xs[0], convert=convert)
    return as_quant_vec(xs, convert=convert)

def show_quantity(x: Numeric | Symbolic, digits=NICE_DIGITS) -> str:
    if isinstance(x, Symbolic):
        return str(x)
    return show_nice_numeric(x, digits)

def show_quantities(xs: Iterable[Numeric | Symbolic]) -> list[str]:
    numerics: list[Numeric] = []
    symbols: list[str] = []
    place_at: list[tuple[int, bool]] = []

    n = 0
    for i, x in enumerate(xs):
        if isinstance(x, Symbolic):
            symbols.append(str(x))
            place_at.append((i, False))
        elif x == INFINITY:
            symbols.append("\u221e")
            place_at.append((i, False))
        elif x == NEGATIVE_INFINITY:
            symbols.append("-\u221e")
            place_at.append((i, False))
        elif x is nothing or x is None:
            symbols.append(str(nothing))
            place_at.append((i, False))
        else:
            numerics.append(x)
            place_at.append((i, True))
        n = i + 1
    numbers = show_values(numerics)

    result = []
    sym_ind = 0
    num_ind = 0
    for i in range(n):
        ind, numeric = place_at[i]
        if numeric:
            result.append(numbers[num_ind])
            num_ind += 1
        else:
            result.append(symbols[sym_ind])
            sym_ind += 1

    return result

def show_qtuples(
        tups: Iterable[tuple],
        scalarize=True
) -> list[str]:
    "Convert a list of tuples to strings with angle-bracket syntax, with a shared representation for each component."
    # if dim == 1:
    #     return show_values([tup[0] for tup in tups], max_denom, exclude_denoms, rounding_mask, rounding)

    # Transpose, Format, and Transpose back
    outT = []
    for out in zip_longest(*tups, fillvalue=nothing):
        outT.append(show_quantities(out))
    dim = len(outT)
    if scalarize and dim == 1:
        return [components[0] for components in zip(*outT)]  # , strict=True
    return [f'<{", ".join(components)}>' for components in zip(*outT)]  # , strict=True

def show_qtuple(
        tup: tuple,
        scalarize=True
) -> str:
    "Show a tuple with angle bracket syntax, but drop brackets for scalars."
    if scalarize and len(tup) == 1:
        return show_quantity(tup[0])
    components = [show_quantity(x) for x in tup]
    return f'<{", ".join(components)}>'


#
# Info tags
#

setattr(qvec, '__info__', 'utilities')
setattr(as_quantity, '__info__', 'utilities')
