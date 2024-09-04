from __future__ import annotations

import inspect
import math
import re
import textwrap

from collections.abc   import Iterable, Collection
from decimal           import Decimal
from functools         import wraps
from math              import prod
from operator          import itemgetter
from typing            import Callable, cast, Literal, Optional, overload, Union
from typing_extensions import Self, TypeAlias, TypeGuard

from frplib.exceptions import OperationError, StatisticError, DomainDimensionError, InputError
from frplib.numeric    import (ScalarQ, Numeric, as_real, numeric_sqrt, numeric_exp,
                               numeric_ln, numeric_log10, numeric_log2,
                               numeric_abs, numeric_floor, numeric_ceil)

from frplib.protocols  import Projection, Transformable
from frplib.quantity   import as_quant_vec, as_quantity
from frplib.symbolic   import Symbolic
from frplib.utils      import identity, is_interactive, is_tuple, scalarize
from frplib.vec_tuples import VecTuple, as_scalar, as_scalar_strict, as_vec_tuple, is_vec_tuple, vec_tuple

# ATTN: conversion with as_real etc in truediv, pow to prevent accidental float conversion
# This could be mitigated by eliminating ints from as_numeric*, but we'll see how this
# goes.


#
# Types
#

ArityType: TypeAlias = tuple[int, Union[int, float]]   # Would like Literal[infinity] here, but mypy rejects
QuantityType: TypeAlias = Union[Numeric, Symbolic]

#
# Special Numerical Values
#

infinity = math.inf  # ATTN: if needed, convert to appropriate value component type
pi = PI = math.pi


#
# Internal Constants
#

ANY_TUPLE: ArityType = (0, infinity)


#
# Helpful Utilities
#

def is_true(v) -> bool:
    "Converts the value returned by a Condition to a boolean."
    return (is_vec_tuple(v) and bool(v[0])) or bool(v)

def is_false(v) -> bool:
    "Converts the complement of the value returned by a Condition to a boolean."
    return (is_vec_tuple(v) and not bool(v[0])) or not bool(v)


#
# Helpers
#

def _codim_str(arity: ArityType) -> str:
    "Compute a nice string representation of a codim tuple."
    multi_arity = is_tuple(arity)
    if multi_arity and arity[1] == infinity:
        codim = f'[{arity[0]}..)'  # {infinity}
    elif multi_arity and arity[1] == arity[0]:
        codim = f'{arity[0]}'
    elif multi_arity:
        codim = f'[{arity[0]}..{arity[1]}]'
    else:
        codim = f'{arity}'  # ATTN: this case should not happen
    return codim

def _reconcile_codims(stat1: Statistic, stat2: Statistic, op_name: str = '') -> ArityType:
    """Returns largest range of codimensions consistent with both statistics, or raise an error.

    Parameter op_name is included in an error message to identify the
    source of any problem. It is intended to identify the combining
    operation of the two statistics.

    See also `combine_arities`.

    """
    codim1 = stat1.codim
    codim2 = stat2.codim

    lo1, hi1 = codim1
    lo2, hi2 = codim2

    if op_name:
        op = f' (via {op_name})'
    else:
        op = ''

    if hi1 < lo2 or hi2 < lo1:
        raise StatisticError(f'Attempt to combine statistics{op} with incompatible '
                             f'codims {_codim_str(codim1)} and {_codim_str(codim2)}')

    return (max(lo1, lo2), min(hi1, hi2))

def as_scalar_stat(x: ScalarQ | Symbolic):
    "Returns a quantity guaranteed to be a scalar for use in statistical math operations."
    return as_quantity(as_scalar_strict(x))

def stat_label(s: Statistic) -> str:
    name = s.name
    if '__' in name:  # name == '__':
        return name
    return f'{name}(__)'

def compose2(after: 'Statistic', before: 'Statistic') -> 'Statistic':
    lo, hi = after.codim
    if before.dim is None or (before.dim >= lo and before.dim <= hi):
        def composed(*x):
            return after(before(*x))
        return Statistic(composed, codim=before.codim, dim=after.dim,
                         name=f'{after.name}({stat_label(before)})')
    raise OperationError(f'Statistics {after.name} and {before.name} are not compatible for composition.')

def combine_arities(has_arity, more) -> ArityType:
    """Combines arities of a collection of statistics to find the widest interval consistent with all of them.

    Returns a tuple (lo, hi).  If lo > hi, there is no consistent arity.
    """
    if has_arity is not None:
        arity_low = has_arity.arity[0]
        arity_high = has_arity.arity[1] if has_arity.strict_arity else infinity
    else:
        arity_low = 0
        arity_high = infinity
    for s in more:
        arity_low = max(arity_low, s.arity[0])
        if s.strict_arity:
            arity_high = min(arity_high, s.arity[1])

    return (arity_low, arity_high)


#
# Decorator/Wrapper to make functions auto-uncurry
#

def analyze_domain(fn: Callable) -> ArityType:
    # sig = inspect.signature(fn)
    sig = inspect.Signature.from_callable(fn)
    requires: int = 0
    accepts: Union[int, float] = 0
    for param in sig.parameters.values():
        if param.kind == inspect.Parameter.POSITIONAL_ONLY:
            requires += 1
        elif param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if param.default == inspect.Parameter.empty:
                requires += 1
            else:
                accepts += 1
        elif param.kind == inspect.Parameter.VAR_POSITIONAL:
            accepts = infinity   # No upper bound
            break
    return (requires, requires + accepts)

def tuple_safe(fn: Callable, *, arities: Optional[int | ArityType] = None, strict=True) -> Callable:
    """Returns a function that can accept a single tuple or multiple individual arguments.

    Ensures that the returned function has an `arity` attribute set
    to the supplied or computed arity.

    If arities is None and fn accepts only one argument, it is imputed that
    any tuple dimension is allowed.

    If strict is False, the retured function accepts a tuple of dimension
    higher than the upper arity. If strict is True, the argument dimension
    must fall within the specified range.

    """
    try:
        fn_accepts = analyze_domain(fn)
    except ValueError:
        fn_accepts = (1, 1)  # Some builtins are not inspectable (e.g., max, min)

    # Should we wrap args into a single tuple or pass multiple args?
    # We cannot distinguish the (1, k) case for 1 < k < infinity
    # as the argument could be a tuple or a scalar. Here, we impute it
    # it as tuple case both because that is more common and because
    # we can easily specify a scalar explicitly if desired.
    single_arg = fn_accepts == (1, 1) or (fn_accepts[0] == 1 and 1 < fn_accepts[1] < infinity)
    if arities is None:
        if single_arg:  # Inferred scalar
            # Cannot distinguish these two cases, prefer the more expansive version
            arities = ANY_TUPLE
        else:
            arities = fn_accepts
    elif isinstance(arities, int):
        arities = (arities, arities)

    if arities == ANY_TUPLE and not (single_arg or fn_accepts == ANY_TUPLE):
        raise InputError(f'The function being wrapped should be able to accept '
                         f'any dimension tuple, instead accepts dimensions {fn_accepts[0]} to {fn_accepts[1]}.')
    elif not single_arg and arities[0] < fn_accepts[0]:
        raise InputError(f'The function being wrapped requires at least {fn_accepts[0]} arguments'
                         f' but should accept {arities[0]} < {fn_accepts[0]} arguments.')
    elif not single_arg and arities[1] > fn_accepts[1]:
        raise InputError(f'The function being wrapped allows at most {fn_accepts[1]} arguments'
                         f' but should accept up to {arities[1]} > {fn_accepts[1]} arguments.')

    # ATTN: We sacrifice DRYness here to avoid doing the single_arg test
    # at each call of the function, of which there can be millions
    # and to avoid facially invalid code in branches within the function.
    # This may be silly, and probably is. If determined to be,
    # just replace e.g., as_quant_vec(fn(x)) with
    #   as_quant_vec(fn(x)) if single_arg else as_quant_vec(fn(*x))
    # in the copies below in the single_arg branchings.
    # Simplfying this is likely a good idea as we already do several
    # tests and conversions in these functions anyway. For now,
    # consider this a simple transitional check on the new logic.
    # CRG 23-Aug-2024

    if arities == ANY_TUPLE:
        if single_arg:
            @wraps(fn)
            def f(*x):
                if len(x) == 1 and is_tuple(x[0]):
                    return as_vec_tuple(fn(x[0]))
                return as_quant_vec(fn(x))
        else:
            @wraps(fn)
            def f(*x):
                if len(x) == 1 and is_tuple(x[0]):
                    return as_vec_tuple(fn(*x[0]))
                return as_quant_vec(fn(*x))
        setattr(f, 'arity', arities)
        setattr(f, 'strict_arity', strict)
        return f
    elif arities == (1, 1):
        # In this case, we accept multiple arguments so that
        # any error (when strict is True, say) can be given
        # nicely in the playground and so that it works when
        # strict is False as it does with the other arities.
        @wraps(fn)
        def g(*x):
            if len(x) == 0 or (strict and len(x) > 1):
                raise DomainDimensionError(f'A function (probably a Statistic) '
                                           f'expects one scalar argument {len(x)} given.')
            if is_tuple(x[0]):
                nargs = len(x[0])
                if nargs == 0 or (strict and nargs > 1):
                    raise DomainDimensionError(f'A function (probably a Statistic) '
                                               f'expects a scalar argument, but a tuple'
                                               f' of dimension {nargs} was given.')
                arg = x[0][0]
            else:
                arg = x[0]
            return as_quant_vec(fn(arg))
        setattr(g, 'arity', arities)
        setattr(g, 'strict_arity', strict)
        return g
    elif arities[1] == infinity:
        if single_arg:
            @wraps(fn)
            def h(*x):
                if len(x) == 1 and is_tuple(x[0]):
                    args = x[0]
                else:
                    args = x
                if len(args) < arities[0]:
                    raise DomainDimensionError(f'A function (probably a Statistic)'
                                               f' expects input of dimension at least {arities[0]}'
                                               f' dimension {len(args)} was given.')
                return as_quant_vec(fn(args))
        else:
            @wraps(fn)
            def h(*x):
                if len(x) == 1 and is_tuple(x[0]):
                    args = x[0]
                else:
                    args = x
                if len(args) < arities[0]:
                    raise DomainDimensionError(f'A function (probably a Statistic)'
                                               f' expects input of dimension at least {arities[0]}'
                                               f' dimension {len(args)} was given.')
                return as_quant_vec(fn(*args))
        setattr(h, 'arity', arities)
        setattr(h, 'strict_arity', strict)
        return h

    if single_arg:
        @wraps(fn)
        def ff(*x):
            if len(x) == 1 and is_tuple(x[0]):
                args = x[0]
            else:
                args = x
            nargs = len(args)
            if nargs < arities[0]:
                raise DomainDimensionError(f'A function (probably a Statistic)'
                                           f' expects input of dimension at least {arities[0]}'
                                           f' dimension {nargs} was given.')
            if strict and nargs > arities[1]:
                raise DomainDimensionError(f'A function (probably a Statistic)'
                                           f' expects input of dimension at most {arities[1]}'
                                           f' but dimension {nargs} was given.')

            take = cast(int, min(arities[1], nargs))  # Implicit project if not strict

            return as_quant_vec(fn(tuple(args[:take])))
    else:
        @wraps(fn)
        def ff(*x):
            if len(x) == 1 and is_tuple(x[0]):
                args = x[0]
            else:
                args = x
            nargs = len(args)
            if nargs < arities[0]:
                raise DomainDimensionError(f'A function (probably a Statistic)'
                                           f' expects input of dimension at least {arities[0]}'
                                           f' but dimension {len(args)} was given.')
            if strict and nargs > arities[1]:
                raise DomainDimensionError(f'A function (probably a Statistic)'
                                           f' expects input of dimension at most {arities[1]}'
                                           f' but dimension {nargs} was given.')

            take = cast(int, min(arities[1], nargs))  # Implicit project if not strict

            return as_quant_vec(fn(*args[:take]))
    setattr(ff, 'arity', arities)
    setattr(ff, 'strict_arity', strict)
    return ff

def old_tuple_safe(fn: Callable, arity: Optional[int] = None) -> Callable:
    """Returns a function that can accept a single tuple or multiple individual arguments.

    Ensures that the returned function has an `arity` attribute set
    to the supplied or computed arity.
    """
    if arity is None:
        arity = len([param for param in inspect.signature(fn).parameters.values()
                     if param.kind <= inspect.Parameter.POSITIONAL_OR_KEYWORD])
    if arity == 0:
        @wraps(fn)
        def f(*x):
            if len(x) == 1 and is_tuple(x[0]):
                return as_vec_tuple(fn(x[0]))
            return as_vec_tuple(fn(x))
        setattr(f, 'arity', arity)
        return f
    elif arity == 1:
        @wraps(fn)
        def g(x):
            if is_tuple(x) and len(x) == 1:
                return as_vec_tuple(fn(x[0]))
            return as_vec_tuple(fn(x))
        setattr(g, 'arity', arity)
        return g

    @wraps(fn)
    def h(*x):
        select = itemgetter(*range(arity))
        if len(x) == 1 and is_tuple(x[0]):
            return as_vec_tuple(fn(*select(x[0])))
        return as_vec_tuple(fn(*select(x)))
    setattr(h, 'arity', arity)
    return h


#
# The Statistics Interface
#

# ATTN: Also implement things like __is__ and __in__ so we can do X ^ (__ in {0, 1, 2})

class Statistic:
    """A transformation of an FRP or Kind.

    A statistic is built from a function that operates on the values of an FRP.
    Here, we treat only the case where the values are (vector-style) tuples
    of arbitrary dimension.

    Constructor Parameters
    ----------------------

    """
    def __init__(
            self: Self,
            fn: Callable | 'Statistic',               # Either a Statistic or a function to be turned into one
            codim: Optional[int | ArityType] = None,  # Codimension (dimension of the domain)
                                                      # (a, b) means fn accepts a <= n <= b args; a means (a, a)
                                                      # infinity allowed for b; None means infer by inspection
                                                      # 0 is taken as a shorthand for ANY_TUPLE
            dim: Optional[int] = None,                # Dimension (of the codomain); None means don't know
            name: Optional[str] = None,               # A user-facing name for the statistic
            description: Optional[str] = None,        # A description used as a __doc__ string for the Statistic
            strict=True                               # If False, implicitly project down onto allowed inputs
    ) -> None:
        if codim == 0:
            codim = ANY_TUPLE

        if isinstance(fn, Statistic):
            if codim is None and strict == fn.strict_arity:
                # Shared wrapped function, same dim and strictness
                self.fn: Callable = fn.fn
                self.arity: ArityType = fn.arity
                self.strict_arity: bool = strict
            elif hasattr(fn.fn, '__wrapped__'):  # from @wraps
                # Rewrap the original function with new dim and/or strictness
                fn_prime = tuple_safe(getattr(fn.fn, '__wrapped__'), arities=dim, strict=strict)
                self.fn = fn_prime
                self.arity = getattr(fn_prime, 'arity')
                self.strict_arity = getattr(fn_prime, 'strict_arity')
            else:  # Anomalous case, do our best, but this won't enforce
                if isinstance(codim, int):
                    codim = (codim, codim)
                self.fn = fn.fn
                self.arity = codim if codim is not None else fn.arity
                self.strict_arity = strict

            self.dim: Optional[int] = dim if dim is not None else fn.dim
            self._name = name or fn.name
            self.__doc__: str = self.__describe__(description or fn.description or '')
            return

        f = tuple_safe(fn, arities=codim, strict=strict)
        self.fn = f
        self.arity = getattr(f, 'arity')
        self.strict_arity = getattr(f, 'strict_arity')
        self.dim = dim
        self._name = name or fn.__name__ or ''
        self.__doc__ = self.__describe__(description or fn.__doc__ or '')

    def __describe__(self, description: str, returns: Optional[str] = None) -> str:
        def splitPascal(pascal: str) -> str:
            return re.sub(r'([a-z])([A-Z])', r'\1 \2', pascal)

        my_name = splitPascal(self.__class__.__name__)
        an = 'An' if re.match(r'[AEIOU]', my_name) else 'A'
        me = f'{an} {my_name} \'{self.name}\''
        that = '' if description else ' that '
        descriptor = ' that ' + (description + '. It ' if description else '')

        scalar = ''
        if not returns:
            if self.dim == 1:
                scalar = 'returns a scalar'
            elif self.dim is not None:
                scalar = f'returns a {self.dim}-tuple'
        else:
            scalar = returns

        arity = ''
        if self.arity[1] == infinity:
            arity = 'expects a tuple'
            if self.arity[0] > 0:
                arity += f' of at least dimension {self.arity[0]}'
        elif self.arity[0] == self.arity[1]:
            if self.arity[0] == 0:  # This makes no sense
                arity = 'expects an empty tuple'
            arity = (f'expects {self.arity[0]} argument{"s" if self.arity[0] > 1 else ""}'
                     ' (or a tuple of that dimension)')

        conj = ' and ' if scalar and arity else that if scalar else ''
        structure = f'{arity}{conj}{scalar}.'

        return f'{me}{descriptor}{structure}'

    def __str__(self) -> str:
        return self.__doc__

    def __repr__(self) -> str:
        if is_interactive():  # Needed?
            return str(self)
        # ATTN! This looks like a bug
        return super().__repr__()

    @property
    def name(self) -> str:
        return self._name

    @property
    def codim(self) -> ArityType:
        "Returns the codimension of the statistic, a tuple representing a closed interval (lo, hi)."
        # if self.arity[0] == self.arity[1]:
        #     return self.arity[0]
        return self.arity

    @property
    def type(self):
        codim = _codim_str(self.arity)
        dim = f'{self.dim}' if self.dim is not None else '*'

        return f'{codim} -> {dim}'

    @property
    def description(self) -> str:
        return self.__doc__

    def __call__(self, *args):
        # It is important that Statistics are not Transformable!
        if len(args) == 1:
            if isinstance(args[0], Transformable):
                return args[0].transform(self)
            if isinstance(args[0], Statistic):
                return compose2(self, args[0])
        return self.fn(*args)

    # Comparisons (macros would be nice here)

    def __eq__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_eq_b(*x):
                return self(*x) == other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '==')
        elif callable(other):
            f = tuple_safe(other)

            def a_eq_b(*x):
                return self(*x) == f(*x)
            label = str(other)
        else:
            def a_eq_b(*x):
                return self(*x) == other
            label = str(other)
            codim = self.codim

        # Break inheritance rules here, but it makes sense!
        return Condition(a_eq_b, codim=codim, name=f'{stat_label(self)} == {label}')

    def __ne__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_ne_b(*x):
                return self(*x) != other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '!=')
        elif callable(other):
            f = tuple_safe(other)

            def a_ne_b(*x):
                return self(*x) != f(*x)
            label = str(other)
        else:
            def a_ne_b(*x):
                return self(*x) != other
            label = str(other)
            codim = self.codim

        # Break inheritance rules here, but it makes sense!
        return Condition(a_ne_b, codim=codim, name=f'{stat_label(self)} != {label}')

    # ATTN:FIX labels for methods below, so e.g., ForEach(2*__+1) prints out nicely

    def __le__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_le_b(*x):
                return self(*x) <= other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '<=')
        elif callable(other):
            f = tuple_safe(other)

            def a_le_b(*x):
                return self(*x) <= f(*x)
            label = str(other)
        else:
            def a_le_b(*x):
                return self(*x) <= other
            label = str(other)
            codim = self.codim

        # Break inheritance rules here, but it makes sense!
        return Condition(a_le_b, codim=codim, name=f'{stat_label(self)} <= {label}')

    def __lt__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_lt_b(*x):
                return self(*x) < other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '<')
        elif callable(other):
            f = tuple_safe(other)

            def a_lt_b(*x):
                return self(*x) < f(*x)
            label = str(other)
        else:
            def a_lt_b(*x):
                return self(*x) < other
            label = str(other)
            codim = self.codim

        # Break inheritance rules here, but it makes sense!
        return Condition(a_lt_b, codim=codim, name=f'{stat_label(self)} < {label}')

    def __ge__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_ge_b(*x):
                return self(*x) >= other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '>=')
        elif callable(other):
            f = tuple_safe(other)

            def a_ge_b(*x):
                return self(*x) >= f(*x)
            label = str(other)
        else:
            def a_ge_b(*x):
                return self(*x) >= other
            label = str(other)
            codim = self.codim

        # Break inheritance rules here, but it makes sense!
        return Condition(a_ge_b, codim=codim, name=f'{stat_label(self)} >= {label}')

    def __gt__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_gt_b(*x):
                return self(*x) > other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '>')
        elif callable(other):
            f = tuple_safe(other)

            def a_gt_b(*x):
                return self(*x) > f(*x)
            label = str(other)
        else:
            def a_gt_b(*x):
                return self(*x) > other
            label = str(other)
            codim = self.codim

        # Break inheritance rules here, but it makes sense!
        return Condition(a_gt_b, codim=codim, name=f'{stat_label(self)} > {label}')

    # Numeric Operations (still would like macros)

    def __add__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_plus_b(*x):
                return self(*x) + other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '+')
        elif callable(other):
            f = tuple_safe(other)

            def a_plus_b(*x):
                return self(*x) + as_quant_vec(f(*x))
            label = str(other)
        else:
            def a_plus_b(*x):
                return self(*x) + as_quant_vec(other)
            label = str(other)
            codim = self.codim

        return Statistic(a_plus_b, codim=codim, name=f'{stat_label(self)} + {label}')

    def __radd__(self, other):
        codim = self.codim
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)

            def a_plus_b(*x):
                return f(*x) + as_quant_vec(self(*x))
            label = str(other)
        else:
            def a_plus_b(*x):
                return other + as_quant_vec(self(*x))
            label = str(other)

        return Statistic(a_plus_b, codim=codim, name=f'{label} + {stat_label(self)}')

    def __sub__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_minus_b(*x):
                return self(*x) - other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '-')
        elif callable(other):
            f = tuple_safe(other)

            def a_minus_b(*x):
                return self(*x) - as_quant_vec(f(*x))
            label = str(other)
        else:
            def a_minus_b(*x):
                return self(*x) - as_quant_vec(other)
            label = str(other)
            codim = self.codim

        return Statistic(a_minus_b, codim=codim, name=f'{stat_label(self)} - {label}')

    def __rsub__(self, other):
        codim = self.codim
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)

            def a_minus_b(*x):
                return f(*x) - as_quant_vec(self(*x))
        else:
            def a_minus_b(*x):
                return other - as_quant_vec(self(*x))

        return Statistic(a_minus_b, codim=codim, name=f'{str(other)} - {stat_label(self)}')

    def __mul__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_times_b(*x):
                return self(*x) * other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '*')
        elif callable(other):
            f = tuple_safe(other)

            def a_times_b(*x):
                return self(*x) * as_scalar_stat(f(*x))
            label = str(other)
        else:
            def a_times_b(*x):
                return self(*x) * as_scalar_stat(other)  # ATTN!
            label = str(other)
            codim = self.codim

        return Statistic(a_times_b, codim=codim, name=f'{stat_label(self)} * {label}')

    def __rmul__(self, other):
        codim = self.codim
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)

            def a_times_b(*x):
                return f(*x) * as_scalar_stat(self(*x))
        else:
            def a_times_b(*x):
                return as_scalar_stat(other) * self(*x)

        return Statistic(a_times_b, codim=codim, name=f'{str(other)} * {stat_label(self)}')

    def __truediv__(self, other):
        codim: int | ArityType = 0
        if isinstance(other, Statistic):
            def a_div_b(*x):
                return self(*x) / other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '/')
        elif callable(other):
            f = tuple_safe(other)

            def a_div_b(*x):
                return self(*x) / f(*x)
            label = str(other)
        else:
            def a_div_b(*x):
                return self(*x) / as_real(as_scalar_strict(other))
            label = str(other)
            codim = self.codim

        return Statistic(a_div_b, codim=codim, name=f'{stat_label(self)} / {label}')

    def __rtruediv__(self, other):
        codim = self.codim
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)

            def a_div_b(*x):
                return as_quantity(f(*x)) / self(*x)
        else:
            def a_div_b(*x):
                return as_quantity(other) / as_quantity(as_scalar_strict(self(*x)))  # type: ignore

        return Statistic(a_div_b, codim=codim, name=f'{str(other)} / {stat_label(self)}')

    def __floordiv__(self, other):
        codim = self.codim
        if isinstance(other, Statistic):
            def a_div_b(*x):
                return self(*x) // other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '//')
        elif callable(other):
            f = tuple_safe(other)

            def a_div_b(*x):
                return self(*x) // as_scalar_stat(f(*x))
            label = str(other)
        else:
            def a_div_b(*x):
                return self(*x) // as_scalar_stat(other)
            label = str(other)

        return Statistic(a_div_b, codim=codim, name=f'{stat_label(self)} // {label}')

    def __rfloordiv__(self, other):
        codim = self.codim
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)

            def a_div_b(*x):
                return f(*x) // as_scalar_stat(self(*x))
        else:
            def a_div_b(*x):
                return other // as_scalar_stat(self(*x))

        return Statistic(a_div_b, codim=codim, name=f'{str(other)} // {stat_label(self)}')

    def __mod__(self, other):
        codim = self.codim
        if isinstance(other, Statistic):
            def a_mod_b(*x):
                return self(*x) % other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '%')
        elif callable(other):
            f = tuple_safe(other)

            def a_mod_b(*x):
                return self(*x) % as_scalar_stat(f(*x))
            label = str(other)
        elif self.dim == 1:
            def a_mod_b(*x):
                try:
                    return scalarize(self(*x)) % as_quantity(other)
                except Exception as e:
                    raise OperationError(f'Could not compute {self.name} % {other}: {str(e)}')
            label = str(other)
        else:
            def a_mod_b(*x):
                val = self(*x)
                if len(val) != 1:
                    raise OperationError(f'Statistic {self.name} is not a scalar but % requires it; '
                                         'try using Proj or Scalar explicitly.')
                try:
                    return scalarize(self(*x)) % as_quantity(other)
                except Exception as e:
                    raise OperationError(f'Could not compute {self.name} % {other}: {str(e)}')
            label = str(other)
        return Statistic(a_mod_b, codim=codim, name=f'{stat_label(self)} % {label}')

    def __rmod__(self, other):
        codim = self.codim
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)

            def a_mod_b(*x):
                return as_quantity(f(*x)) % scalarize(self(*x))
        else:
            def a_mod_b(*x):
                return as_quantity(other) % scalarize(self(*x))

        return Statistic(a_mod_b, codim=codim, name=f'{str(other)} % {stat_label(self)}')

    def __pow__(self, other):
        codim = self.codim
        if isinstance(other, Statistic):
            def a_pow_b(*x):
                return self(*x) ** other(*x)
            label = stat_label(other)
            codim = _reconcile_codims(self, other, '**')
        elif callable(other):
            f = tuple_safe(other)

            def a_pow_b(*x):
                return self(*x) ** as_quantity(f(*x))
            label = str(other)
        else:
            def a_pow_b(*x):
                return self(*x) ** as_quantity(other)
            label = str(other)

        return Statistic(a_pow_b, codim=codim, name=f'{stat_label(self)} ** {label}')

    def __rpow__(self, other):
        codim = self.codim
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)

            def a_pow_b(*x):
                return as_quantity(f(*x)) ** self(*x)
        else:
            def a_pow_b(*x):
                return as_quantity(other) ** self(*x)

        return Statistic(a_pow_b, codim=codim, name=f'{str(other)} ** {stat_label(self)}')

    def __xor__(self, other):
        "Chained composition of two statistics, self then other"
        if not isinstance(other, Statistic):
            return NotImplemented
        return compose2(other, self)

def is_statistic(x) -> TypeGuard[Statistic]:
    return isinstance(x, Statistic)

def scalar_fn(stat: Statistic) -> Callable:
    "Converts a statistic into a regular scalar function."
    def as_fn(val):
        return as_scalar_strict(stat(val))
    return as_fn

class MonoidalStatistic(Statistic):
    def __init__(
            self,
            fn: Callable | 'Statistic',               # Either a Statistic or a function to be turned into one
            unit,                                     # The unit of the monoid
            codim: Optional[int | ArityType] = None,  # (a, b) means fn accepts a <= n <= b args; a means (a, a)
                                                      # infinity allowed for b; None means infer by inspection
            dim: Optional[int] = None,                # Dimension (of the codomain); None means don't know
            name: Optional[str] = None,               # A user-facing name for the statistic
            description: Optional[str] = None,        # A description used as a __doc__ string for the Statistic
            strict=True                               # If true, then strictly enforce dim upper bound
    ) -> None:
        super().__init__(fn, codim, dim, name, description, strict=strict)
        self.unit = as_vec_tuple(unit)

    def __call__(self, *args):
        if len(args) == 0:
            return self.unit
        return super().__call__(*args)

class ProjectionStatistic(Statistic, Projection):
    """Special statistics that extract one or more components from the tuple passed as input.

    This class should not be used directly but only through the Proj statistic factory.
    See `Proj` and Chapter 0, Section 2.3.

    """
    def __init__(
            self,
            # ATTN: Don't need this here, just adapt project; ATTN: No need for fn here!
            fn: Callable | 'Statistic',          # Either a Statistic or a function to be turned into one
            onto: Iterable[int] | slice | Self,  # 1-indexed projection indices
            name: Optional[str] = None           # A user-facing name for the statistic
    ) -> None:
        codim: Optional[int | ArityType] = 0
        dim = None
        if isinstance(onto, ProjectionStatistic):
            indices: Iterable[int] | slice | 'ProjectionStatistic' = onto.subspace
            dim = onto.dim
            label = onto.name.replace('project[', '').replace(']', '')

        if isinstance(onto, Iterable):
            indices = list(onto)
            codim = (max(0, max(indices)), infinity)
            dim = len(indices)
            label = ", ".join(map(str, indices))
            if any([index == 0 for index in indices]):  # Negative from the end OK
                raise StatisticError('Projection indices are 1-indexed and must be non-zero')
        elif isinstance(onto, slice):
            indices = onto
            has_step = indices.step is None
            label = (f'{indices.start or ""}:{indices.stop or ""}{":" if has_step else ""}'
                     f'{indices.step if has_step else ""}')
            # ATTN: Already converted in project; need to merge this
            # if indices.start == 0 or indices.stop == 0:
            #     raise StatisticError('Projection indices are 1-indexed and must be non-zero')

        description = textwrap.wrap(f'''A statistic that projects any value of dimension >= {codim or 1}
                                        to extract the {dim} components with indices {label}.''')
        # ATTN: Just pass project here, don't take an fn arg!
        super().__init__(fn, codim, dim, name, '\n'.join(description))
        self._components = indices

    @property
    def subspace(self):
        return self._components

    # ATTN: Make project() below a method here
    # ATTN?? Add minimum_dim property that specifies minimum compatible dimension;
    # e.g., Project[3] -> 3, Project[2:-1] -> 2, Project[1,3,5] -> 5

def _ibool(x) -> Literal[0, 1]:
    return 1 if bool(x) else 0

class Condition(Statistic):
    """A condition is a statistic that returns a boolean value.

    Boolean values here are represented in the output with
    0 for false and 1 for true, though the input callable
    can return any
    """
    def __init__(
            self,
            predicate: Callable | 'Statistic',        # Either a Statistic or a function to be turned into one
            codim: Optional[int | ArityType] = None,  # (a, b) means fn accepts a <= n <= b args; a means (a, a)
                                                      # infinity allowed for b; None means infer by inspection
            name: Optional[str] = None,               # A user-facing name for the statistic
            description: Optional[str] = None,        # A description used as a __doc__ string for the Statistic
            strict=True                               # If true, then strictly enforce dim upper bound
    ) -> None:
        super().__init__(predicate, codim, 1, name, description, strict)
        self.__doc__ = self.__describe__(description or predicate.__doc__ or '', 'returns a 0-1 (boolean) value')

    def __call__(self, *args) -> tuple[Literal[0, 1], ...] | Statistic:
        if len(args) == 1 and isinstance(args[0], Transformable):
            return args[0].transform(self)
        if isinstance(args[0], Statistic):
            return Condition(compose2(self, args[0]))
        result = super().__call__(*args)
        return as_vec_tuple(_ibool(as_scalar(result)))  # type: ignore
        # if is_vec_tuple(result):
        #     return result.map(_ibool)
        # return as_vec_tuple(result).map(_ibool)

    def bool_eval(self, *args) -> bool:
        result = self(*args)
        if isinstance(result, tuple):
            return bool(result[0])
        elif isinstance(result, (bool, int, Decimal, str)):
            return bool(result)
        raise StatisticError(f'Attempt to check an unevaluated Condition/Statistic {result.name}')


#
# Statistic decorator for easily creating a statistic out of a function
#

def statistic(
        maybe_fn: Optional[Callable] = None,  # If supplied, return Statistic, else a decorator
        *,
        name: Optional[str] = None,               # A user-facing name for the statistic
        codim: Optional[int | ArityType] = None,  # Codimension (i.e., dimension of the domain)
                                                  # (a, b) means fn accepts a <= n <= b args; a means (a, a)
                                                  # infinity allowed for b; None means infer by inspection
        dim: Optional[int] = None,                # Dimension (of the codomain); None means don't know
        description: Optional[str] = None,        # A description used as a __doc__ string for the Statistic
        monoidal=None,                            # If not None, the unit for a Monoidal Statistic
        strict=True,                              # If true, then strictly enforce dim upper bound
        arg_convert: Optional[Callable] = None    # If not None, a function applies to every input component
) -> Statistic | Callable[[Callable], Statistic]:
    """
    Statistics factory and decorator. Converts a function into a Statistic.

    Can take the function as a first argument or be used as a decorator on a def.

    """

    if maybe_fn is not None:
        if monoidal is None:
            s = Statistic(maybe_fn, codim, dim, name, description, strict=strict)
        else:
            s = MonoidalStatistic(maybe_fn, monoidal, codim, dim, name, description, strict=strict)

        if arg_convert is not None:
            convert = Statistic(lambda v: map(arg_convert, v), codim=s.codim)   # type: ignore
            s = compose2(s, convert)
        return s

    if arg_convert is not None:
        if monoidal is None:
            def decorator(fn: Callable) -> Statistic:     # Function to be converted to a statistic
                s = Statistic(fn, codim, dim, name, description, strict=strict)
                convert = Statistic(lambda v: map(arg_convert, v), codim=s.codim)
                return compose2(s, convert)
        else:
            def decorator(fn: Callable) -> Statistic:     # Function to be converted to a statistic
                s = MonoidalStatistic(fn, monoidal, codim, dim, name, description, strict=strict)
                convert = Statistic(lambda v: map(arg_convert, v), codim=s.codim)
                return compose2(s, convert)
    elif monoidal is None:
        def decorator(fn: Callable) -> Statistic:     # Function to be converted to a statistic
            return Statistic(fn, codim, dim, name, description, strict=strict)
    else:
        def decorator(fn: Callable) -> Statistic:     # Function to be converted to a statistic
            return MonoidalStatistic(fn, monoidal, codim, dim, name, description, strict=strict)
    return decorator

def scalar_statistic(
        maybe_fn: Optional[Callable] = None,      # If supplied, return Statistic, else a decorator
        *,
        name: Optional[str] = None,               # A user-facing name for the statistic
        codim: Optional[int | ArityType] = None,  # (a, b) means fn accepts a <= n <= b args; a means (a, a)
                                                  # infinity allowed for b; None means infer by inspection
        description: Optional[str] = None,        # A description used as a __doc__ string for the Statistic
        monoidal=None,                            # If not None, the unit of a Monoidal Statistic
        strict=True                               # If true, then strictly enforce dim upper bound
        # ATTN: could add arg_convert here too
):
    """
    Statistics factory and decorator. Converts a function into a Statistic that returns a scalar.

    Can take the function as a first argument or be used as a decorator on a def.

    """
    return statistic(maybe_fn, name=name, codim=codim, dim=1,
                     description=description, monoidal=monoidal, strict=strict)

def condition(
        maybe_predicate: Optional[Callable] = None,  # If supplied, return Condition, else a decorator
        *,
        name: Optional[str] = None,         # A user-facing name for the statistic
        codim: Optional[int] = None,        # Number of arguments the function takes; 0 means tuple expected
        description: Optional[str] = None,  # A description used as a __doc__ string for the Statistic
        strict=True                         # If true, then strictly enforce dim upper bound
) -> Condition | Callable[[Callable], Condition]:
    """
    Statistics factory and decorator. Converts a predicate into a Condition statistic.

    Can take the function as a first argument or be used as a decorator on a def.

    """
    if maybe_predicate:
        return Condition(maybe_predicate, codim, name, description, strict=strict)

    def decorator(predicate: Callable) -> Condition:     # Function to be converted to a statistic
        return Condition(predicate, codim, name, description, strict=strict)
    return decorator


#
# Statistics Combinators
#

def fork(*statistics: Statistic) -> Statistic:
    """Statistic combinator. Produces a new statistic that combines others statistics' results in a tuple.

    This is equivalent to the Fork combinator.
    """
    # ATTN: Only one of fork and Fork are needed
    d = len(statistics)
    if d == 0:
        StatisticError('The fork combinator requires at least one and preferably two statistics, none given.')
    if d == 1:
        return statistics[0]

    arity_lo, arity_hi = combine_arities(None, statistics)  # Arities must all be consistent

    if arity_lo > arity_hi:
        raise DomainDimensionError(f'fork must be called on statistics of consistent codimension,'
                                   f' found min {arity_lo} > max {arity_hi}.')
    codim = (arity_lo, arity_hi)
    dim: Optional[int] = 0
    if all(s.dim is not None and s.dim > 0 for s in statistics):
        dim = sum(s.dim for s in statistics)  # type: ignore
    if dim == 0:
        dim = None

    def forked(*x):
        returns = []
        for s in statistics:
            returns.extend(s(*x))
        return as_quant_vec(returns)
    names = ", ".join([s.name for s in statistics])
    return Statistic(forked, codim=codim, dim=dim,
                     name=f'fork({names})',
                     description=f'returns a tuple of the results of ({names})')

def chain(*statistics: Statistic) -> Statistic:
    "Statistic combinator. Compose statistics in pipeline order: (f ; g)(x) = g(f(x)), read 'f then g'."
    if len(statistics) == 0:
        return Id
    elif len(statistics) == 1:
        return statistics[0]

    in_dim = statistics[0].dim
    for s in statistics[1:]:
        if in_dim is None or s.arity[0] <= in_dim <= s.arity[1]:
            in_dim = s.dim
            continue
        raise DomainDimensionError(f'chain requires compatible statistics, '
                                   f'input dimension {in_dim} does not match {s.arity}.')

    def chained(*x):
        state = x
        for stat in statistics:
            state = stat(*state)
        return state

    arity = statistics[0].arity
    names = ", ".join([stat.name for stat in statistics])
    return Statistic(chained, arity, name=f'chain({names})')

def compose(*statistics: Statistic) -> Statistic:
    "Statistic Combinator. Compose statistics in mathematical order: (f o g)(x) = f(g(x)), read 'f after g'."
    if len(statistics) == 0:
        return Id
    elif len(statistics) == 1:
        return statistics[0]

    rev_statistics = list(statistics)
    rev_statistics.reverse()

    in_dim = rev_statistics[0].dim
    for s in rev_statistics[1:]:
        if in_dim is None or s.arity[0] <= in_dim <= s.arity[1]:
            in_dim = s.dim
            continue
        raise DomainDimensionError(f'compose requires compatible statistics, '
                                   f'input dimension {in_dim} does not match {s.arity}.')

    def composed(*x):
        state = x
        for stat in rev_statistics:
            state = stat(*state)
        return state
    arity = rev_statistics[0].arity
    names = ", ".join([stat.name for stat in statistics])
    return Statistic(composed, arity, name=f'compose({names})')


#
# Commonly Used Statistics
#

Id = Statistic(identity, codim=ANY_TUPLE, name='identity', description='returns the value given as is')
Scalar = Statistic(lambda x: x[0] if is_tuple(x) else x, codim=1, dim=1, strict=True,
                   name='scalar', description='represents a scalar value')
__ = Statistic(identity, codim=ANY_TUPLE, name='__', description='represents the value given to the statistic')
_x_ = Scalar

# def Constantly(x) -> Statistic:
#     "A statistic factory that produces a statistic that always returns `x`."
#     xvec = as_quant_vec(x)
#     return Statistic(lambda _: xvec, codim=ANY_TUPLE, dim=len(xvec), name=f'The constant {xvec}')
def Constantly(*x) -> Statistic:
    """A statistic factory that produces a statistic that always returns the specified value.

    This accepts either a single tuple argument, which will be converted to a quantity vector,
    or multiple arguments that will be aggregated into a quantity vector.

    """
    if len(x) == 1 and is_tuple(x[0]):
        xvec = as_quant_vec(x[0])
    else:
        xvec = as_quant_vec(x)
    return Statistic(lambda _: xvec, codim=ANY_TUPLE, dim=len(xvec), name=f'The constant {xvec}')

Sum = MonoidalStatistic(sum, unit=0, codim=0, dim=1, name='sum',
                        description='returns the sum of all the components of the given value')
Product = MonoidalStatistic(prod, unit=1, codim=0, dim=1, name='product',
                            description='returns the product of all the components of the given value')
Count = MonoidalStatistic(len, unit=0, codim=0, dim=1, name='count',
                          description='returns the number of components in the given value')
Max = MonoidalStatistic(max, unit=as_quantity('-infinity'), codim=0, dim=1, name='max',
                        description='returns the maximum of all components of the given value')
Min = MonoidalStatistic(min, unit=as_quantity('infinity'), codim=0, dim=1, name='min',
                        description='returns the minimum of all components of the given value')
Mean = Statistic(lambda x: sum(x) / as_real(len(x)), codim=0, dim=1, name='mean',
                 description='returns the arithmetic mean of all components of the given value')
Floor = Statistic(numeric_floor, codim=1, dim=1, name='floor',
                  description='returns the greatest integer <= its argument')
Ceil = Statistic(numeric_ceil, codim=1, dim=1, name='ceiling',
                 description='returns the least integer >= its argument')

Sqrt = Statistic(numeric_sqrt, codim=1, dim=1, name='sqrt', strict=True,
                 description='returns the square root of a scalar argument')
Exp = Statistic(numeric_exp, codim=1, dim=1, name='exp', strict=True,
                description='returns the exponential of a scalar argument')
Log = Statistic(numeric_ln, codim=1, dim=1, name='log', strict=True,
                description='returns the natural logarithm of a positive scalar argument')
Log2 = Statistic(numeric_log2, codim=1, dim=1, name='log', strict=True,
                 description='returns the logarithm base 2 of a positive scalar argument')
Log10 = Statistic(numeric_log10, codim=1, dim=1, name='log', strict=True,
                  description='returns the logarithm base 10 of a positive scalar argument')
# ATTN: Can use the decimal recipes for sin and cos
Sin = Statistic(math.sin, codim=1, dim=1, name='sin', strict=True,
                description='returns the sine of a scalar argument')
Cos = Statistic(math.cos, codim=1, dim=1, name='cos', strict=True,
                description='returns the cosine of a scalar argument')
Tan = Statistic(math.tan, codim=1, dim=1, name='tan', strict=True,
                description='returns the tangent of a scalar argument')
Sinh = Statistic(math.sinh, codim=1, dim=1, name='sin', strict=True,
                 description='returns the hyperbolic sine of a scalar argument')
Cosh = Statistic(math.cosh, codim=1, dim=1, name='cos', strict=True,
                 description='returns the hyperbolic cosine of a scalar argument')
Tanh = Statistic(math.tanh, codim=1, dim=1, name='tan', strict=True,
                 description='returns the hyperbolic tangent of a scalar argument')

# Make Abs act like Norm for larger dimensions
# Abs = Statistic(numeric_abs, codim=1, dim=1, name='abs',
#                 description='returns the absolute value of the given number')
@statistic(codim=(1, infinity), dim=1, name='abs',
           description='returns the absolute value of the given number or the modulus of a tuple')
def Abs(x):
    if len(x) == 1:
        return numeric_abs(x[0])
    return numeric_sqrt(sum(u * u for u in x))

def Dot(*vec):
    if len(vec) == 1 and is_tuple(vec[0]):
        v: Collection[QuantityType] = vec[0]
    elif len(vec) > 0:
        v = vec
    else:
        raise StatisticError('Statistic factory Dot requires quantity tuple of dimension >= 1')

    @statistic(codim=len(v), dim=1, name='dot',
               description=f'returns dot product with vector {as_vec_tuple(v)}')
    def dot(x):
        return sum(xi * vi for xi, vi in zip(x, v))

    return dot

@statistic
def Ascending(v):
    "returns the components of its input in increasing order"
    return sorted(v)

@statistic
def Descending(v):
    "returns the components of its input in decreasing order"
    return sorted(v, reverse=True)

@scalar_statistic(name='atan2', codim=(1, 2), description='returns the sector correct arctangent')
def ATan2(x, y=1):
    return as_quantity(math.atan2(x, y))

Pi = Decimal('3.1415926535897932384626433832795')

@scalar_statistic(codim=1)
def FromDegrees(degs):
    "converts a scalar in degrees to radians"
    return Pi * degs / 180

@scalar_statistic(codim=1)
def FromRadians(rads):
    "converts a scalar in radians to degrees"
    return 180 * rads / Pi

@scalar_statistic(name='Phi', codim=1, strict=True,
                  description='returns the cumulative distribution function of the standard Normal distribution')
def NormalCDF(x):
    'Cumulative distribution function for the standard normal distribution'
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

@statistic(name='sumsq', monoidal=0, description='returns the sum of squares of components')
def SumSq(value):
    return sum(v * v for v in value)

@scalar_statistic(name='norm', codim=(1, infinity), description='returns the Euclidean norm of its argument')
def Norm(value):
    return numeric_sqrt(sum(v * v for v in value))

@scalar_statistic(name='sd', codim=(1, infinity),
                  description='returns the sample standard deviation of the values components')
def StdDev(value):
    n = len(value)
    if n == 1:
        return 0
    mu = as_scalar(Mean(value))
    return numeric_sqrt(sum((v - mu) ** 2 for v in value) / as_real(n - 1))

@scalar_statistic(name='variance', codim=(1, infinity),
                  description='returns the sample variance of the values components')
def Variance(value):
    n = len(value)
    if n == 1:
        return 0
    mu = as_scalar(Mean(value))
    return sum((v - mu) ** 2 for v in value) / as_real(n - 1)

@scalar_statistic(name='argmax', codim=(1, infinity))
def ArgMax(val):
    'returns the index of the maximum component of a non-empty tuple'
    max_ind = 0
    max_val = val[0]
    for i in range(1, len(val)):
        if val[i] > max_val:
            max_ind = i
            max_val = val[i]
    return max_ind

@statistic(name='argmin', codim=(1, infinity))
def ArgMin(val):
    'returns the index of the minimum component of a non-empty tuple'
    min_ind = 0
    min_val = val[0]
    for i in range(1, len(val)):
        if val[i] < min_val:
            min_ind = i
            min_val = val[i]
    return min_ind

@statistic(name='diff', codim=(1, infinity))
def Diff(xs):
    'returns tuple of first differences of a non-empty tuple'
    n = len(xs)
    if n < 2:
        return vec_tuple()
    diffs = []
    for i in range(1, n):
        diffs.append(xs[i] - xs[i - 1])
    return as_quant_vec(diffs)

def Diffs(k: int):
    "Statistics factory. Produces a statistic to compute `k`-th order diffs of its argument"

    def diffk(xs):
        n = len(xs)
        if n < k + 1:
            return vec_tuple()

        diffs = list(xs)
        for _ in range(k):
            target = diffs
            diffs = []
            n_target = len(target)
            for i in range(1, n_target):
                diffs.append(target[i] - target[i - 1])
        return as_quant_vec(diffs)

    return Statistic(diffk, codim=(1, infinity), name=f'diffs[{k}]',
                     description=f'returns order {k} differences of its argument')


#
# Combinators
#

def ForEach(s: Statistic) -> Statistic:
    """Statistics combinator. Produces a statistic that applies another statistic to each component of its argument.

    This is typically applied to scalar statistics, where each application corresponds to one component,
    but it accepts higher dim statistics. In this case, the tuples produced by the statistics
    are concatenated in the result tuple.
    """
    def foreach(*x):
        if len(x) > 0 and is_tuple(x[0]):
            x = x[0]
        result = []
        for xi in x:
            result.extend(s(xi))
        return as_quant_vec(result)
    return Statistic(foreach, codim=ANY_TUPLE, name=f'applies {s.name} to every component of input value')

def Fork(stat: Statistic | ScalarQ, *other_stats: Statistic | ScalarQ) -> Statistic:
    """Statistics combinator. Produces a statistic that combines the values of other statistics into a tuple.

    If a statistic has dim > 1, the results are spliced into the tuple resulting from Fork.

    Examples:

      + Fork(__, __ + 2, 2 * __ ) produes a statistic that takes a value x and returns <x, x + 2, 2 * x>.
      + Fork(Sum, Diff) produces a statistic that takes a tuple <x, y, z> and returns
            <x + y + z, y - x, z - y>
      + Fork(__, __) produces a statistic that takes a value <x1,x2,...,xn> and returns
            the tuple <x1,x2,...,xn,x1,x2,...,xn>

    """
    # Treat constants like statistics
    if not isinstance(stat, Statistic):
        stat = Constantly(as_quantity(stat))
    more_stats: list[Statistic] = [s if isinstance(s, Statistic) else Constantly(as_quantity(s))
                                   for s in other_stats]

    if len(more_stats) == 0:
        return stat

    arity_lo, arity_hi = combine_arities(stat, more_stats)  # Arities must all be consistent

    if arity_lo > arity_hi:
        raise DomainDimensionError(f'Fork must be called on statistics of consistent codimension,'
                                   f' found min {arity_lo} > max {arity_hi}.')
    codim = (arity_lo, arity_hi)
    dim: Optional[int] = 0
    if stat.dim is not None and stat.dim > 0 and all(s.dim is not None and s.dim > 0 for s in more_stats):
        dim = stat.dim + sum(s.dim for s in more_stats)  # type: ignore
    if dim == 0:
        dim = None

    def forked(*x):
        returns = []
        returns.extend(stat(*x))
        for s in more_stats:
            returns.extend(s(*x))
        return as_quant_vec(returns)

    return Statistic(forked, codim=codim, dim=dim,
                     name=f'fork({stat.name}, {", ".join([s.name for s in more_stats])})')

def MFork(stat: MonoidalStatistic | ScalarQ, *other_stats: MonoidalStatistic | ScalarQ) -> MonoidalStatistic:
    "Like Fork, but takes and returns Monoidal Statistics."
    return cast(MonoidalStatistic, Fork(stat, *other_stats))

# ATTN: fix up (cycle notation and straight) but keeping it simple for now
def _find_cycles(inds: list[int], drop_singletons=True) -> list[list[int]]:
    """Find a list of cycles in 0-based index list by cycle convention

    Cycles are arranged in order of increasing biggest element with the
    biggest element first. Indices are 0-based and non-negative.

    """
    cycles = []
    max_so_far = -1
    thresh = 1 if drop_singletons else 0
    current: list[int] = []
    for ind in inds:
        if ind > max_so_far:
            max_so_far = ind
            if len(current) > thresh:
                cycles.append(current)
            current = [ind]
        else:
            current.append(ind)
    if len(current) > thresh:
        cycles.append(current)
    return cycles


def Permute(*p: int | tuple[int, ...], cycle=True):
    """A statistics factory that produces permutation statistics.

    Accepts a list of (1-indexed) component indices (either as
    individual arguments or as a single iterable).
    By default, indices are interpreted as a cycle specification,
    i.e., cycle=True.

    If cycle=True, the indices are interpreted as a cycle
    specification, where each cycle is listed with
    its largest element first and cycles are listed
    in increasing orderof their largest element.

    For example, Permute(4, 2, 7, 3, 1, 5, cycle=True)
    maps <1, 2, ..., 8> to <3, 4, 7, 2, 1, 6, 5, 8>,
    with cycles (42) and (7315).

    Similarly, Permute(3, 1, 2) takes the third element
    to position one, the first to position two, and 
    the second to position three.

    If cycle=False, the indices should contain all values 1..n
    exactly once for some positive integer n. Each index indicates
    which value of the input vector goes in that position.

    For example, Permute(4, 2, 7, 3, 1, 5, 6, cycle=False)
    maps <1, 2, ..., 8> to <4, 2, 7, 3, 1, 5, 6, 8>.

    Similarly, Permute(3, 2, 1) means that the original 3rd
    component is first and the original 1st component is third.
    Similarly, Permute(3, 1, 2) rearranges in the order third,
    first, second.

    In either case, if m is the maximum index given,
    then the permutation has codimension k for every k >= m.
    Values above the maximum index are left in their original
    place.

    More Examples:

    + Permute(3, 1, 4, 2) takes <a, b, c, d> to <c, d, a, b>
    + Permute(4, 1, 2, 3, cycle=False) takes <a, b, c, d> to <d, a, b, c>

    """

    # Move to 0-indexed base for internal calculations
    if len(p) == 1 and is_tuple(p[0]):
        p_realized = [k - 1 for k in p[0]]
    else:
        p_realized = [k - 1 for k in cast(tuple[int], p)]
    p_max = max(p_realized)
    n = p_max + 1    # Minimum codimension

    if cycle:
        cycles = _find_cycles(p_realized)
        @statistic(name='permute', codim=(n, infinity))
        def permute(value):
            permuted = list(value)
            for c in cycles:  # c has len > 1
                n_c = len(c)
                for i in range(1, n_c):
                    permuted[c[i]] = value[c[i-1]]
                permuted[c[0]] = value[c[n_c - 1]]
            return VecTuple(permuted)
        return permute

    n_unique = len(set(p_realized))
    if n_unique < n:
        raise StatisticError('Non-cycle Permute specification should contain '
                             f'all indices from 1 to {n}')
    if n_unique < len(p_realized):
        raise StatisticError('Permute specification contains repeated indices')

    # pos = list(range(n))
    # iperm = list(range(n))
    # perm = list(range(n))
    # print('---', pos)
    # for i, k in enumerate(p_realized):
    #     pi = pos[i]
    #     perm[i] = k
    #     pos[i] = pos[k]
    #     pos[k] = i
    #     print('+++', k, i, pos)
    # perm = [pos[i] for i in range(n)]
    # print('>>>', perm, pos)

    # # ATTN
    # Old
    perm = p_realized

    @statistic(name='permute', codim=(n, infinity))
    def permute_direct(value):
        m = len(value)
        # if m < n:
        #     raise StatisticError(f'Permutation of {n} items applied to tuple of dimension {m} < {n}.')
        return VecTuple(value[perm[i]] if i < n else value[i] for i in range(m))
    return permute_direct

def IfThenElse(
        cond: Statistic,
        t: Statistic | tuple | float | int,
        f: Statistic | tuple | float | int,
) -> Statistic:
    """Statistics combinator. Produces a statistic that uses one statistic to choose which other statistic to apply.

    Parameters
    ----------
    `cond` :: A condition or any scalar statistic; it's value will be interpreted by
        ordinary python boolean rules. To avoid, accidentally getting a truthy value
        because a tuple of dimension > 1 is returned, this statistic should return
        a scalar value only.
    `t` :: A statistic to apply if `cond` returns a truthy value
    `f` :: A statistic to apply if `cond` returns a falsy value.

    All three statistics should have consistent codimensions.

    Returns a new statistic with the largest possible range of codimensions.

    """
    if not is_statistic(t):
        t = Constantly(t)
    if not is_statistic(f):
        f = Constantly(f)

    arity_lo, arity_hi = combine_arities(cond, [t, f])
    if arity_lo > arity_hi:
        raise DomainDimensionError(f'IfThenElse must be called on statistics of consistent codimension,'
                                   f' found min {arity_lo} > max {arity_hi}.')

    if t.dim is not None and f.dim is not None and t.dim != f.dim:
        raise StatisticError('True and False statistics for IfElse must have matching dims')

    def ifelse(*x):
        if as_scalar_strict(cond(*x)):
            return t(*x)
        else:
            return f(*x)
    return Statistic(ifelse, codim=cond.arity, dim=t.dim,
                     name=f'returns {t.name} if {cond.name} is true else returns {f.name}')

def Not(s: Statistic) -> Condition:
    """Statistics combinator. Resulting statistic takes the logical Not of the given statistic.

    Returns a Condition which produces a 0 or 1 for False or True.

    """
    if s.dim is not None and s.dim != 1:
        raise DomainDimensionError(f'Not should be applied only to a scalar statistic or condition,'
                                   f' given a statistic of dimension {s.dim}.')
    return Condition(lambda *x: 1 - s(*x), codim=s.arity, name=f'not({s.name})',
                     description=f'returns the logical not of {s.name}')

def And(*stats: Statistic) -> Condition:
    """Statistic combinator. Resulting statistic takes the (short-circuiting) logical And of all the given statistics.

    Returns a Condition which produces a 0 or 1 for False or True.

    """
    arity_lo, arity_hi = combine_arities(None, stats)
    if arity_lo > arity_hi:
        raise DomainDimensionError(f'And must be called on statistics of consistent codimension,'
                                   f' found min {arity_lo} > max {arity_hi}.')
    # ATTN: require si.codim == 1

    def and_of(*x):
        val = True
        for s in stats:
            val = val and bool(as_scalar_stat(s(*x)))
            if not val:
                break
        return val
    labels = ["'" + s.name + "'" for s in stats]
    return Condition(and_of, codim=(arity_lo, arity_hi),
                     name=f'({" and ".join(labels)})',
                     description=f'returns the logical and of {", ".join(labels)}')

def Or(*stats: Statistic) -> Condition:
    """Statistic combinator. Resulting statistic takes the (short-circuiting) logical Or of all the given statistics.

    Returns a Condition which produces a 0 or 1 for False or True.

    """
    arity_lo, arity_hi = combine_arities(None, stats)
    if arity_lo > arity_hi:
        raise DomainDimensionError(f'Or must be called on statistics of consistent codimension,'
                                   f' found min {arity_lo} > max {arity_hi}.')
    # ATTN: require si.codim == 1

    def or_of(*x):
        val = False
        for s in stats:
            val = val or bool(as_scalar_stat(s(*x)))
            if val:
                break
        return val
    labels = ["'" + s.name + "'" for s in stats]
    return Condition(or_of, codim=(arity_lo, arity_hi),
                     name=f'({" or ".join(labels)})',
                     description=f'returns the logical or of {", ".join(labels)}')

def Xor(*stats: Statistic) -> Condition:
    """Statistic combinator. Logical exclusive or of one or more statistics.

    Returns a Condition which produces a 0 or 1 for False or True.

    The resulting statistic takes the logical Exclusive-Or of all the given statistics.
    Since this requires that exactly one statistic give a truthy value it is not
    short circuiting.

    """
    arity_lo, arity_hi = combine_arities(None, stats)
    if arity_lo > arity_hi:
        raise DomainDimensionError(f'Xor must be called on statistics of consistent codimension,'
                                   f' found min {arity_lo} > max {arity_hi}.')
    # ATTN: require si.codim == 1

    def xor_of(*x):
        val = False
        for s in stats:
            result = bool(as_scalar_stat(s(*x)))
            if val and result:
                return False
            val = result
        return val
    labels = ["'" + s.name + "'" for s in stats]
    return Condition(xor_of, codim=(arity_lo, arity_hi),
                     name=f'({" xor ".join(labels)})',
                     description=f'returns the logical exclusieve-or of {", ".join(labels)}')

top = Condition(lambda _x: True, name='top', description='returns true for any value')

bottom = Condition(lambda _x: False, name='bottom', description='returns false for any value')


# ATTN: These should really be methods of ProjectionStatistic
# There should be no need for a callable argment in that constructor.
@overload
def project(*__indices: int) -> ProjectionStatistic:
    ...

@overload
def project(__index_tuple: Iterable[int]) -> ProjectionStatistic:
    ...

def project(*indices_or_tuple) -> ProjectionStatistic:
    """Creates a projection statistic that extracts the specified components.

       Positional variadic arguments:
         *indices_or_tuple -- a tuple of integer indices starting from 1 or a single int tuple

    """
    if len(indices_or_tuple) == 0:  # ATTN:Error here instead?
        return ProjectionStatistic(lambda _: (), (), name='Null projection')

    # In that sense, it would be good if the projection statistic could also get
    # the dimension of the input tuple, then we could use Proj[2:-1] to mean
    # all but the first and Proj[1:-2] for all but the last regardless of
    # dimension.

    if isinstance(indices_or_tuple[0], slice):
        def dec_or_none(x: int | None) -> int | None:
            if x is not None and x > 0:
                return x - 1
            return x
        zindexed = indices_or_tuple[0]
        indices: slice | Iterable = slice(dec_or_none(zindexed.start),
                                          dec_or_none(zindexed.stop),
                                          zindexed.step)

        def get_indices(xs):
            return as_vec_tuple(xs[indices])
        label = str(indices)
    else:
        if isinstance(indices_or_tuple[0], Iterable):
            indices = indices_or_tuple[0]
        else:
            indices = indices_or_tuple

        def get_indices(xs):
            getter = itemgetter(*[x - 1 if x > 0 else x for x in indices if x != 0])
            return as_vec_tuple(getter(xs))
        label = ", ".join(map(str, indices))
    return ProjectionStatistic(
        get_indices,
        indices,
        name=f'project[{label}]')


class ProjectionFactory:
    """Creates a Projection Statistic.

    Projections are statistics that extract one or more components
    from the tuple passed as input.
    
    In frplib, `Proj` is a factory for creating projection statistics.
    We specify which projection is produced by indicating the
    components in brackets, like indexing an array. The components
    for a projection statistic are **1-based**, so the first component
    has index 1 (not 0 like in Python).
    
    So for example, `Proj[1]` is the projection that returns the
    first component of a tuple and `Proj[1, 3, 5]` returns a new
    tuple with the first, third, and fifth components of its argument.
    
    The `Proj` factory supports a variety of ways to select components.
    The following forms can be used within the `[]` brackets:
    
    + a single, positive integer `i` selects the ith component
    + a single, negative integer `-i` selects the ith component
      *from the end*, with -1 being the last componet, -2 the
      second to last, and so forth.
    + a list of non-zero integers selects the corresponding
      components in order and puts them in a new tuple.
      Both positive and negative indices can be used, and indices
      can be repeated.
    + a slice of the form `i:j` selects all components from `i`
      up to but not including `j`. This works with both positive
      and negative indices, so `Proj[2:-1]` extracts all but
      the first and last components.
    + a slice with one side missing, either `i:` or `:j`.
      The former selects from `i` to the end; the latter
      from the beginning up to but not including `j`.
    + a slice with skip `i:j:k` selects from `i` up to 
      but not including `j`, skipping by `k` components
      at each step.
    
    The `Projbar` factory is like `Proj` but the specification
    in brackets indicates which components to *exclude*.
    
    See Chapter 0, Section 2.3 for more detail.

    """
    @overload
    def __call__(self, *__indices: int) -> ProjectionStatistic:
        ...

    @overload
    def __call__(self, __index_tuple: Iterable[int]) -> ProjectionStatistic:
        ...

    @overload
    def __call__(self, __index_slice: slice) -> ProjectionStatistic:
        ...

    def __call__(self, *indices_or_tuple) -> ProjectionStatistic:
        return project(*indices_or_tuple)

    @overload
    def __getitem__(self, *__indices: int) -> ProjectionStatistic:
        ...

    @overload
    def __getitem__(self, __index_tuple: Iterable[int]) -> ProjectionStatistic:
        ...

    @overload
    def __getitem__(self, __index_slice: slice) -> ProjectionStatistic:
        ...

    def __getitem__(self, *indices_or_tuple) -> ProjectionStatistic:
        return project(*indices_or_tuple)

Proj = ProjectionFactory()


#
# Info tags
#

setattr(statistic, '__info__', 'statistic-factories')
setattr(scalar_statistic, '__info__', 'statistic-factories')
setattr(condition, '__info__', 'statistic-factories')
setattr(Constantly, '__info__', 'statistic-factories')
setattr(Permute, '__info__', 'statistic-factories')
setattr(Proj, '__info__', 'statistic-factories::projections')


setattr(__, '__info__', 'statistic-builtins')
setattr(Id, '__info__', 'statistic-builtins')
setattr(Scalar, '__info__', 'statistic-builtins')

setattr(Sum, '__info__', 'statistic-builtins')
setattr(Count, '__info__', 'statistic-builtins')
setattr(Min, '__info__', 'statistic-builtins')
setattr(Max, '__info__', 'statistic-builtins')
setattr(ArgMin, '__info__', 'statistic-builtins')
setattr(ArgMax, '__info__', 'statistic-builtins')
setattr(Mean, '__info__', 'statistic-builtins')
setattr(Ascending, '__info__', 'statistic-builtins')
setattr(Descending, '__info__', 'statistic-builtins')
setattr(Diff, '__info__', 'statistic-builtins')
setattr(Diffs, '__info__', 'statistic-builtins')
setattr(Abs, '__info__', 'statistic-builtins')
setattr(Sqrt, '__info__', 'statistic-builtins')
setattr(Floor, '__info__', 'statistic-builtins')
setattr(Ceil, '__info__', 'statistic-builtins')
setattr(Exp, '__info__', 'statistic-builtins')
setattr(Log, '__info__', 'statistic-builtins')
setattr(Log2, '__info__', 'statistic-builtins')
setattr(Log10, '__info__', 'statistic-builtins')
setattr(Sin, '__info__', 'statistic-builtins')
setattr(Cos, '__info__', 'statistic-builtins')
setattr(Tan, '__info__', 'statistic-builtins')
setattr(ATan2, '__info__', 'statistic-builtins')
setattr(Sinh, '__info__', 'statistic-builtins')
setattr(Cosh, '__info__', 'statistic-builtins')
setattr(Tanh, '__info__', 'statistic-builtins')
setattr(FromDegrees, '__info__', 'statistic-builtins')
setattr(FromRadians, '__info__', 'statistic-builtins')
setattr(NormalCDF, '__info__', 'statistic-builtins')
setattr(SumSq, '__info__', 'statistic-builtins')
setattr(Norm, '__info__', 'statistic-builtins')
setattr(Dot, '__info__', 'statistic-builtins')
setattr(StdDev, '__info__', 'statistic-builtins')
setattr(Variance, '__info__', 'statistic-builtins')

setattr(Fork, '__info__', 'statistic-combinators')
setattr(MFork, '__info__', 'statistic-combinators')
setattr(ForEach, '__info__', 'statistic-combinators')
setattr(IfThenElse, '__info__', 'statistic-combinators')
setattr(And, '__info__', 'statistic-combinators')
setattr(Or, '__info__', 'statistic-combinators')
setattr(Not, '__info__', 'statistic-combinators')
setattr(Xor, '__info__', 'statistic-combinators')
