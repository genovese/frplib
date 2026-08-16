"""Functions for creating and displaying quantities.

In frplib, quantities are entities that can be in the components of
a numeric value (i.e., tuple). These include integers,
high-precision decimals, symbolic quantities, and the special item
nothing.

A variety of types can be converted to quantities, including
a range of numeric types, strings, booleans, and nothing.

The user-facing function `tup` is used to flexibly create
vector-tuples of quantities, converting liberally (e.g.,
strings '4/9' and Booleans True and Fraction objects).

"""

from __future__ import annotations

import re

from collections.abc   import Iterable
from decimal           import Decimal
from fractions         import Fraction
from itertools         import zip_longest
from typing            import Callable, TypeGuard, overload

from frplib.exceptions import NumericConversionError
from frplib.numeric    import (Numeric, NumericQ, NumericQuantity, ScalarQ, nothing, Nothing,
                               as_nice_numeric, as_numeric, as_real, is_scalar_q,
                               numeric_q_from_str, show_values, show_nice_numeric)
from frplib.symbolic   import Symbolic, is_symbolic, symbol
from frplib.vec_tuples import VecTuple, vec_tuple


INFINITY = numeric_q_from_str('Infinity').value
NEGATIVE_INFINITY = numeric_q_from_str('-Infinity').value

def is_quantity(x) -> TypeGuard[int | Decimal | Symbolic | Nothing]:
    """Is the given value a `quantity` (numeric, symbolic, or nothing)?"""
    return isinstance(x, (int, Decimal)) or is_symbolic(x) or x == nothing

def is_quantifiable(x) -> TypeGuard[
        int | float | Fraction | Decimal | NumericQ | Symbolic | Nothing | str | bool
]:
    """Is the given value convertible to a `quantity`?

    This is true for any value for which as_quantity returns a valid quantity.
    This includes various numeric types (int, float, Fraction, Decimal, NumericQuantity)
    as well as Symbolic values and Nothing.

    """
    return is_scalar_q(x) or is_symbolic(x) or x is nothing

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
        x=0,
        convert_numeric=as_numeric  # as_nice_numeric  # ATTN: as_numeric instead??
):
    """Converts a quantifiable entity into an frplib quantity.

    Quantifiables include numeric values (int, float, Fraction, Decimal, bool),
    strings, symbols, and the special nothing item.

    Parameters

    x: the entity to be converted into a quantity

    convert_numeric: the function used to do numeric conversion
        when x has a numeric type (default: as_numeric)

    This raises an error if x is not quantifiable.

    Returns the converted quantity.

    """
    if isinstance(x, Symbolic):
        return x

    if isinstance(x, str):
        if re.match(r'\s*[-+.0-9]', x) or re.match(r'(?i)-?inf(?:inity)?', x):
            return convert_numeric(numeric_q_from_str(x))
        if x.lower() == 'nothing':
            return nothing
        return symbol(x)

    if isinstance(x, Nothing):
        return nothing

    if isinstance(x, bool):
        return int(x)

    if is_scalar_q(x):
        return convert_numeric(x)

    raise NumericConversionError(f'as_quantity: could not convert {x} to a quantity')

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
    """Like as_quantity but specialized to convert numeric to RealQuantity objects."""
    return as_quantity(x, convert_numeric=as_real)

def as_nice_quantity(x: ScalarQ | Symbolic) -> Numeric | Symbolic | Nothing:
    """Like as_quantity but with an aesthetically gentler numeric conversion."""
    return as_quantity(x, convert_numeric=as_nice_numeric)

def as_quant_vec(x, convert=as_quantity):
    "Converts an iterable or a value into a vector-style tuple with numerics or symbols."
    # ATTN: Consider using as_real for the convert_numeric in as_quantity
    if isinstance(x, Iterable) and not isinstance(x, str):
        return VecTuple(map(convert, x))
    return vec_tuple(convert(x))

def qvec(*xs, convert=as_quantity):
    "Wraps its arguments in a quantitative vector. If given a single iterable, converts that instead."
    if len(xs) == 0:
        return vec_tuple()
    if len(xs) == 1 and isinstance(xs[0], Iterable) and not isinstance(xs[0], str):
        return as_quant_vec(xs[0], convert=convert)
    return as_quant_vec(xs, convert=convert)

tup = qvec  # NOTE: tup is the user-facing version we will use henceforth, allows specialization later

def show_quantity(x: Numeric | Symbolic | Nothing, digits=None) -> str:
    """Converts a single quantity to a string, hopefully in a pleasant way."""
    if isinstance(x, Symbolic):
        return str(x)
    if isinstance(x, Nothing):
        return str(nothing)
    return show_nice_numeric(x, digits=digits)

def show_quantities(xs: Iterable[Numeric | Nothing | Symbolic]) -> list[str]:
    """Converts a collection of quantities to a list of strings, hopefully in a pleasant way."""
    numerics: list[Numeric | Nothing] = []
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
        _ind, numeric = place_at[i]
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
    """Converts a list of tuples to strings with angle-bracket syntax, with a shared component representation."""
    # if dim == 1:
    #     return show_values([tup[0] for tup in tups], max_denom, exclude_denoms, rounding_mask, rounding)

    # Transpose, Format, and Transpose back
    out_t = []
    for out in zip_longest(*tups, fillvalue=nothing):
        out_t.append(show_quantities(out))
    dim = len(out_t)
    if scalarize and dim == 1:
        return [components[0] for components in zip(*out_t)]  # , strict=True
    return [f'<{", ".join(components)}>' for components in zip(*out_t)]  # , strict=True

def show_qtuple(
        tupl: tuple,
        scalarize=True
) -> str:
    """Shows a tuple with angle bracket syntax, but drop brackets for scalars."""
    if scalarize and len(tupl) == 1:
        return show_quantity(tupl[0])
    components = [show_quantity(x) for x in tupl]
    return f'<{", ".join(components)}>'


#
# Info tags
#

setattr(qvec, '__info__', 'utilities')
setattr(as_quantity, '__info__', 'utilities')
