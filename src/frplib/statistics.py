from __future__ import annotations

import inspect
import math
import re
import textwrap

from collections.abc   import Iterable
from functools         import wraps
from operator          import itemgetter
from typing            import Callable, Literal, Optional, overload
from typing_extensions import Self, TypeGuard

from frplib.exceptions import OperationError, StatisticError
from frplib.numeric    import as_real, as_numeric
from frplib.protocols  import Projection, Transformable
from frplib.utils      import ensure_tuple, identity, is_interactive, is_tuple, scalarize
from frplib.vec_tuples import VecTuple, as_scalar, as_scalar_strict, as_vec_tuple

# ATTN: conversion with as_real etc in truediv, pow to prevent accidental float conversion
# This could be mitigated by eliminating ints from as_numeric*, but we'll see how this
# goes.


#
# Helpers
#


def compose2(after: 'Statistic', before: 'Statistic') -> 'Statistic':
    if after.dim == 0 or before.codim is None or after.dim == before.codim:
        def composed(*x):
            return after(before(*x))
        return Statistic(composed, dim=before.dim, codim=after.codim, name=f'{after.name}({before.name}(__))')
    raise OperationError(f'Statistics {after.name} and {before.name} are not compatible for composition.')


#
# Decorator/Wrapper to make functions auto-uncurry
#

def tuple_safe(fn: Callable, arity: Optional[int] = None) -> Callable:
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

# TODO: Need to handle dimensions of return type.
#       In particular, something like Sum returns a scalar, which needs to be wrapped in a tuple at the end ?!?
#       Also want to allow operations on tuples to be component wise and implement @ as a dot product
#       So,   Id - (1, 2, 3) is a tuple and Id @ (1, 2, 3) is a scalar wrapped
#       Add: Scalar function or wrap scalar constants in operation methods below

# Idea here is to be able to do things like
# dice | Sum > 5 and d6 ** 4 ^ Sum / 4  and d6 ** 4 ^ Mean
# or even dice ^ Sum > 5

# dice | fork(Sum, Count)               # produces tuples x :-> (sum(x), len(x))
# dice | chain(Id - 7, Abs, Id <= 3)    # should reduce to lambda x: |x - 7| <= 3
#
# Built-in statistics: Sum, Mean, Max, Min, Product, Count, Dot(c1,c2,c3,...)
# [dot product, repeat last coefficient ad infinitum; this is a function that produces a Statistic],
# Id, Proj(1,...) [func that produces a statistic, equiv to @ but allows Proj(2) - Proj(1)],
# Permutation(i1,i2,i3,...),
# Square, Cube, SumOfSquares, Sqrt, Pow(exp), Exp, Ln, Abs, Sin, Cos, Tan

# NOTE: This means that we want to accept 0-1 valued functions in conditioning predicates
# as well as boolean functions. Or maybe it's OK and just works, but probably want to convert
# boolean to 0-1 in .map().  <<<---- so events become easy

# Note: codim=0 can be used to mean the same dim as input

# ATTN: Also implement things like __is__ and __in__ so we can do X ^ (__ in {0, 1, 2})

class Statistic:
    "A function that operates on the output of an FRP."
    def __init__(
            self: Self,
            fn: Callable | 'Statistic',         # Either a Statistic or a function to be turned into one
            dim: Optional[int] = None,          # Number of arguments the function takes; 0 means tuple expected
            codim: Optional[int] = None,        # Dimension of the codomain; None means don't know
            name: Optional[str] = None,         # A user-facing name for the statistic
            description: Optional[str] = None   # A description used as a __doc__ string for the Statistic
    ) -> None:
        "Note: set arity to 0 to advise that it takes the whole tuple/vector; None means try to find out"

        if isinstance(fn, Statistic):
            self.fn: Callable = fn.fn
            self.arity: int = dim if dim is not None else fn.arity
            self.codim: Optional[int] = codim if codim is not None else fn.codim
            self._name = name or fn.name
            self.__doc__: str = self.__describe__(description or fn.description or '')
            return

        f = tuple_safe(fn, dim)
        self.fn = f
        self.arity = getattr(f, 'arity')
        self.codim = codim
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
            if self.codim == 1:
                scalar = 'returns a scalar'
            elif self.codim is not None:
                scalar = f'returns a {self.codim}-tuple'
        else:
            scalar = returns

        arity = ''
        if self.arity == 0:
            arity = 'expects a tuple'
        elif self.arity > 0:
            arity = f'expects {self.arity} argument{"s" if self.arity > 1 else ""} (or a tuple of that length)'

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
    def dim(self) -> int:
        "Returns the dimension of the statistic, with 0 meaning it accepts an arbitrary tuple."
        return self.arity

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
        if isinstance(other, Statistic):
            def a_eq_b(*x):
                return self(*x) == other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_eq_b(*x):
                return self(*x) == f(*x)
            label = str(other)
        else:
            def a_eq_b(*x):
                return self(*x) == other
            label = str(other)

        # Break inheritance rules here, but it makes sense!
        return Condition(a_eq_b, dim=0, name=f'{self.name}(__) == {label}')

    def __ne__(self, other):
        if isinstance(other, Statistic):
            def a_ne_b(*x):
                return self(*x) != other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_ne_b(*x):
                return self(*x) != f(*x)
            label = str(other)
        else:
            def a_ne_b(*x):
                return self(*x) != other
            label = str(other)

        # Break inheritance rules here, but it makes sense!
        return Condition(a_ne_b, dim=0, name=f'{self.name}(__) != {label}')

    ## ATTN:FIX labels for methods below, so e.g., ForEach(2*__+1) prints out nicely

    def __le__(self, other):
        if isinstance(other, Statistic):
            def a_le_b(*x):
                return self(*x) <= other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_le_b(*x):
                return self(*x) <= f(*x)
            label = str(other)
        else:
            def a_le_b(*x):
                return self(*x) <= other
            label = str(other)

        # Break inheritance rules here, but it makes sense!
        return Condition(a_le_b, dim=0, name=f'{self.name}(__) <= {label}')

    def __lt__(self, other):
        if isinstance(other, Statistic):
            def a_lt_b(*x):
                return self(*x) < other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_lt_b(*x):
                return self(*x) < f(*x)
            label = str(other)
        else:
            def a_lt_b(*x):
                return self(*x) < other
            label = str(other)

        # Break inheritance rules here, but it makes sense!
        return Condition(a_lt_b, dim=0, name=f'{self.name}(__) < {label}')

    def __ge__(self, other):
        if isinstance(other, Statistic):
            def a_ge_b(*x):
                return self(*x) >= other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_ge_b(*x):
                return self(*x) >= f(*x)
            label = str(other)
        else:
            def a_ge_b(*x):
                return self(*x) >= other
            label = str(other)

        # Break inheritance rules here, but it makes sense!
        return Condition(a_ge_b, dim=0, name=f'{self.name}(__) >= {label}')

    def __gt__(self, other):
        if isinstance(other, Statistic):
            def a_gt_b(*x):
                return self(*x) > other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_gt_b(*x):
                return self(*x) > f(*x)
            label = str(other)
        else:
            def a_gt_b(*x):
                return self(*x) > other
            label = str(other)

        # Break inheritance rules here, but it makes sense!
        return Condition(a_gt_b, dim=0, name=f'{self.name}(__) > {label}')

    # Numeric Operations (still would like macros)

    def __add__(self, other):
        if isinstance(other, Statistic):
            def a_plus_b(*x):
                return self(*x) + other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_plus_b(*x):
                return self(*x) + f(*x)
            label = str(other)
        else:
            def a_plus_b(*x):
                return self(*x) + other
            label = str(other)

        return Statistic(a_plus_b, dim=0, name=f'{self.name}(__) + {label}')

    def __radd__(self, other):
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)
            def a_plus_b(*x):
                return self(*x) + f(*x)
            label = str(other)
        else:
            def a_plus_b(*x):
                return self(*x) + other
            label = str(other)

        return Statistic(a_plus_b, dim=0, name=f'{label} + {self.name}(__)')

    def __sub__(self, other):
        if isinstance(other, Statistic):
            def a_minus_b(*x):
                return self(*x) - other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_minus_b(*x):
                return self(*x) - f(*x)
            label = str(other)
        else:
            def a_minus_b(*x):
                return self(*x) - other
            label = str(other)

        return Statistic(a_minus_b, dim=0, name=f'{self.name}(__) - {label}')

    def __rsub__(self, other):
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)
            def a_minus_b(*x):
                return f(*x) - self(*x)
        else:
            def a_minus_b(*x):
                return other - self(*x)

        return Statistic(a_minus_b, dim=0, name=f'{str(other)} - {self.name}(__)')

    def __mul__(self, other):
        if isinstance(other, Statistic):
            def a_times_b(*x):
                return self(*x) * other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_times_b(*x):
                return self(*x) * f(*x)
            label = str(other)
        else:
            def a_times_b(*x):
                return self(*x) * as_real(as_scalar_strict(other))  # ATTN!
            label = str(other)

        return Statistic(a_times_b, dim=0, name=f'{self.name}(__) * {label}')

    def __rmul__(self, other):
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)
            def a_times_b(*x):
                return self(*x) * f(*x)
        else:
            def a_times_b(*x):
                return self(*x) * as_real(as_scalar_strict(other))

        return Statistic(a_times_b, dim=0, name=f'{str(other)} * {self.name}(__)')

    def __truediv__(self, other):
        if isinstance(other, Statistic):
            def a_div_b(*x):
                return self(*x) / other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_div_b(*x):
                return self(*x) / f(*x)
            label = str(other)
        else:
            def a_div_b(*x):
                return self(*x) / as_real(as_scalar_strict(other))
            label = str(other)

        return Statistic(a_div_b, dim=0, name=f'{self.name}(__) / {label}')

    def __rtruediv__(self, other):
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)
            def a_div_b(*x):
                return f(*x) / self(*x)
        else:
            def a_div_b(*x):
                return other / as_real(as_scalar_strict(self(*x)))

        return Statistic(a_div_b, dim=0, name=f'{str(other)} / {self.name}(__)')

    def __floordiv__(self, other):
        if isinstance(other, Statistic):
            def a_div_b(*x):
                return self(*x) // other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_div_b(*x):
                return self(*x) // f(*x)
            label = str(other)
        else:
            def a_div_b(*x):
                return self(*x) // other
            label = str(other)

        return Statistic(a_div_b, dim=0, name=f'{self.name}(__) // {label}')

    def __rfloordiv__(self, other):
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)
            def a_div_b(*x):
                return f(*x) // self(*x)
        else:
            def a_div_b(*x):
                return other // self(*x)

        return Statistic(a_div_b, dim=0, name=f'{str(other)} // {self.name}(__)')

    def __mod__(self, other):
        if isinstance(other, Statistic):
            def a_mod_b(*x):
                return self(*x) % other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_mod_b(*x):
                return self(*x) % f(*x)
            label = str(other)
        elif self.codim == 1:
            def a_mod_b(*x):
                try:
                    return scalarize(self(*x)) % other
                except Exception as e:
                    raise OperationError(f'Could not compute {self.name} % {other}: {str(e)}')
            label = str(other)
        else:
            def a_mod_b(*x):
                val = self(*x)
                if len(val) != 1:
                    raise OperationError(f'Statistic {self.name} is not a scalar but % requires it; try using Scalar explicitly.')
                try:
                    return scalarize(self(*x)) % other
                except Exception as e:
                    raise OperationError(f'Could not compute {self.name} % {other}: {str(e)}')
            label = str(other)
        return Statistic(a_mod_b, dim=0, name=f'{self.name}(__) % {label}')

    def __rmod__(self, other):
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)
            def a_mod_b(*x):
                return f(*x) % self(*x)
        else:
            def a_mod_b(*x):
                return other % self(*x)

        return Statistic(a_mod_b, dim=0, name=f'{str(other)} % {self.name}(__)')

    def __pow__(self, other):
        if isinstance(other, Statistic):
            def a_pow_b(*x):
                return self(*x) ** other(*x)
            label = f'{other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_pow_b(*x):
                return self(*x) ** f(*x)
            label = str(other)
        else:
            def a_pow_b(*x):
                return self(*x) ** as_numeric(other)
            label = str(other)

        return Statistic(a_pow_b, dim=0, name=f'{self.name}(__) ** {label}')

    def __rpow__(self, other):
        if callable(other):   # other cannot be a Statistic in __r*__
            f = tuple_safe(other)
            def a_pow_b(*x):
                return f(*x) ** self(*x)
        else:
            def a_pow_b(*x):
                return as_numeric(other) ** self(*x)

        return Statistic(a_pow_b, dim=0, name=f'{str(other)} ** {self.name}(__)')

    def __and__(self, other):
        if isinstance(other, Statistic):
            def a_and_b(*x):
                return self(*x) and other(*x)
            label = f'{self.name}(__) and {other.name}'
        elif callable(other):
            f = tuple_safe(other)
            def a_and_b(*x):
                return self(*x) and f(*x)
            label = f'{self.name}(__) and {str(other)}'
        else:
            def a_and_b(*x):
                return self(*x) and other
            label = f'{self.name}(__) and {str(other)}'

        return Statistic(a_and_b, dim=0, name=label)

    def __or__(self, other):
        if isinstance(other, Statistic):
            def a_or_b(*x):
                return self(*x) or other(*x)
            label = f'{self.name}(__) or {other.name}(__)'
        elif callable(other):
            f = tuple_safe(other)
            def a_or_b(*x):
                return self(*x) or f(*x)
            label = f'{self.name}(__) or {str(other)}'
        else:
            def a_or_b(*x):
                return self(*x) or other
            label = f'{self.name} and {str(other)}'

        return Statistic(a_or_b, dim=0, name=label)


def is_statistic(x) -> TypeGuard[Statistic]:
    return isinstance(x, Statistic)

class MonoidalStatistic(Statistic):
    def __init__(self,
                 fn: Callable | 'Statistic',        # Either a Statistic or a function to be turned into one
                 unit,                              # The unit of the monoid
                 dim: Optional[int] = None,       # Number of arguments the function takes; 0 means tuple expected
                 codim: Optional[int] = None,       # Dimension of the codomain; None means don't know
                 name: Optional[str] = None,        # A user-facing name for the statistic
                 description: Optional[str] = None  # A description used as a __doc__ string for the Statistic
                ) -> None:
        super().__init__(fn, dim, codim, name, description)
        self.unit = unit

    def __call__(self, *args):
        if len(args) == 0:
            return self.unit
        return super().__call__(*args)

class ProjectionStatistic(Statistic, Projection):
    def __init__(self,
                 # ATTN: Don't need this here, just adapt project
                 fn: Callable | 'Statistic',         # Either a Statistic or a function to be turned into one ATTN: No need for fn here!
                 onto: Iterable[int] | slice | Self, # 1-indexed projection indices
                 name: Optional[str] = None          # A user-facing name for the statistic
                ) -> None:
        codim = None
        dim = 0
        if isinstance(onto, ProjectionStatistic):
            indices: Iterable[int] | slice | 'ProjectionStatistic' = onto.subspace
            codim = onto.codim
            label = onto.name.replace('project[', '').replace(']', '')

        if isinstance(onto, Iterable):
            indices = list(onto)
            codim = len(indices)
            dim = max(indices)
            label = ", ".join(map(str, indices))
            if any([index == 0 for index in indices]):  # Negative from the end OK
                raise StatisticError('Projection indices are 1-indexed and must be non-zero')
        elif isinstance(onto, slice):
            indices = onto
            has_step = indices.step is None
            label = f'{indices.start or ""}:{indices.stop or ""}{":" if has_step else ""}{indices.step if has_step else ""}'
            # ATTN: Already converted in project; need to merge this
            #if indices.start == 0 or indices.stop == 0:
            #    raise StatisticError('Projection indices are 1-indexed and must be non-zero')
        
        description = textwrap.wrap(f'''A statistic that projects any value of dimension >= {dim or 1}
                                        to extract the {codim} components with indices {label}.''')
        # ATTN: Just pass project here, don't take an fn arg!
        super().__init__(fn, 0, codim, name, '\n'.join(description))
        self._components = indices

    @property
    def subspace(self):
        return self._components

    #ATTN: Make project() below a method here
    #ATTN?? Add minimum_dim property that specifies minimum compatible dimension; e.g., Project[3] -> 3, Project[2:-1] -> 2, Project[1,3,5] -> 5

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
            predicate: Callable | 'Statistic',  # Either a Statistic or a function to be turned into one
            dim: Optional[int] = None,          # Number of arguments the function takes; 0 means tuple expected
            name: Optional[str] = None,         # A user-facing name for the statistic
            description: Optional[str] = None   # A description used as a __doc__ string for the Statistic
    ) -> None:
        super().__init__(predicate, dim, 1, name, description)
        self.__doc__ = self.__describe__(description or predicate.__doc__ or '', 'returns a 0-1 (boolean) value')

    def __call__(self, *args) -> Literal[0, 1] | Statistic:
        if len(args) == 1 and isinstance(args[0], Transformable):
            return args[0].transform(self)
        if isinstance(args[0], Statistic):
            return Condition(compose2(self, args[0]))
        result = super().__call__(*args)
        return _ibool(as_scalar(result))
        # if is_vec_tuple(result):
        #     return result.map(_ibool)
        # return as_vec_tuple(result).map(_ibool)


#
# Statistic decorator for easily creating a statistic out of a function
#

def statistic(
        maybe_fn: Optional[Callable] = None,  # If supplied, return Statistic, else a decorator
        *,
        name: Optional[str] = None,         # A user-facing name for the statistic
        dim: Optional[int] = None,          # Number of arguments the function takes; 0 means tuple expected
        codim: Optional[int] = None,        # Dimension of the codomain; None means don't know
        description: Optional[str] = None,  # A description used as a __doc__ string for the Statistic
        monoidal=None                       # If not None, the unit for a Monoidal Statistic
) -> Statistic | Callable[[Callable], Statistic]:
    """
    """
    if maybe_fn and monoidal is None:
        return Statistic(maybe_fn, dim, codim, name, description)
    elif maybe_fn:
        return MonoidalStatistic(maybe_fn, monoidal, dim, codim, name, description)

    if monoidal is None:
        def decorator(fn: Callable) -> Statistic:     # Function to be converted to a statistic
            return Statistic(fn, dim, codim, name, description)
    else:
        def decorator(fn: Callable) -> Statistic:     # Function to be converted to a statistic
            return MonoidalStatistic(fn, monoidal, dim, codim, name, description)
    return decorator

def scalar_statistic(
        name: Optional[str] = None,         # A user-facing name for the statistic
        dim: Optional[int] = None,          # Number of arguments the function takes; 0 means tuple expected
        description: Optional[str] = None,  # A description used as a __doc__ string for the Statistic
        monoidal=None                     # If not None, the unit of a Monoidal Statistic
):
    def decorator(fn: Callable) -> Statistic:     # Function to be converted to a statistic
        return Statistic(fn, dim, 1, name, description)
    return decorator

def condition(
        maybe_predicate: Optional[Callable] = None,  # If supplied, return Condition, else a decorator
        *,
        name: Optional[str] = None,         # A user-facing name for the statistic
        dim: Optional[int] = None,          # Number of arguments the function takes; 0 means tuple expected
        codim: Optional[int] = None,        # Dimension of the codomain; None means don't know
        description: Optional[str] = None,  # A description used as a __doc__ string for the Statistic
        monoidal=None                     # If not None, the unit for a Monoidal Statistic
) -> Condition | Callable[[Callable], Condition]:
    """
    """
    if maybe_predicate:
        return Condition(maybe_predicate, dim, name, description)

    def decorator(predicate: Callable) -> Condition:     # Function to be converted to a statistic
        return Condition(predicate, dim, name, description)
    return decorator


#
# Statistics Combinators
#

def fork(*statistics: Statistic) -> Statistic:
    arities = {stat.arity for stat in statistics}
    def forked(*x):
        return tuple([stat(*x) for stat in statistics])
    names = [stat.name for stat in statistics]
    return Statistic(forked, dim=next(iter(arities)) if len(arities) == 1 else 0,
                     name=f'fork({", ".join(names)})',
                     description=f'returns a tuple of the results of ({", ".join(names)})')

def chain(*statistics: Statistic) -> Statistic:
    "Compose statistics in pipeline order: (f ; g)(x) = g(f(x)), read 'f then g'."
    # ATTN: check arities compatible etc
    def chained(*x):
        state = x
        for stat in statistics:
            state = stat(*state)
        return state
    arity = statistics[0].arity if len(statistics) > 0 else None
    names = ", ".join([stat.name for stat in statistics])
    return Statistic(chained, arity, name=f'chain({names})')

def compose(*statistics: Statistic) -> Statistic:
    "Compose statistics in mathematical order: (f o g)(x) = f(g(x)), read 'f after g'."
    # ATTN: check dims and codims etc
    rev_statistics = list(statistics)
    rev_statistics.reverse()
    def composed(*x):
        state = x
        for stat in rev_statistics:
            state = stat(*state)
        return state
    arity = rev_statistics[0].arity if len(statistics) > 0 else None
    names = ", ".join([stat.name for stat in statistics])
    return Statistic(composed, arity, name=f'compose({names})')


#
# Special Numerical Values
#

infinity = math.inf  # ATTN: if needed, convert to appropriate value component type


#
# Commonly Used Statistics
#

Id = Statistic(identity, dim=0, name='identity', description='returns the value given as is')
Scalar = Statistic(lambda x: x[0] if is_tuple(x) else x, dim=1, name='scalar', description='represents a scalar value')
__ = Id # ATTN  Make this act like both Id and Scalar
_x_ = Scalar

Sum = MonoidalStatistic(sum, unit=0, dim=0, codim=1, name='sum', description='returns the sum of all the components of the given value')
Count = MonoidalStatistic(len,unit=0, dim=0, codim=1, name='count', description='returns the number of components in the given value')
Max = MonoidalStatistic(max, unit=-math.inf, dim=0, codim=1, name='max', description='returns the maximum of all components of the given value')
Min = MonoidalStatistic(min, unit=math.inf, dim=0, codim=1, name='min', description='returns the minimum of all components of the given value')
Mean = Statistic(lambda x: sum(x)/len(x), dim=0, codim=1, name='mean', description='returns the arithmetic mean of all components of the given value')
Abs = Statistic(abs, dim=1, codim=1, name='abs', description='returns the absolute value of the given number')

# Diff == takes first order diffs of the tuple
# Diffs(k) takes k-order diffs

def Constantly(x) -> Statistic:
    xtuple = ensure_tuple(x)
    return Statistic(lambda _: xtuple, dim=0, codim=len(xtuple), name=f'The constant {xtuple}')

Cos = Statistic(math.cos, dim=1, codim=1, name='cos', description='returns the cosine of a scalar argument')
Sin = Statistic(math.sin, dim=1, codim=1, name='sin', description='returns the sine of a scalar argument')
Exp = Statistic(math.exp, dim=1, codim=1, name='exp', description='returns the exponential of a scalar argument')
Log = Statistic(math.log, dim=1, codim=1, name='log', description='returns the natural logarithm of a positive scalar argument')
Log2 = Statistic(math.log2, dim=1, codim=1, name='log', description='returns the logarithm base 2 of a positive scalar argument')
Log10 = Statistic(math.log2, dim=1, codim=1, name='log', description='returns the logarithm base 10 of a positive scalar argument')


#
# Combinators
#

def ForEach(s: Statistic) -> Statistic:
    def foreach(*x):
        if len(x) > 0 and is_tuple(x[0]):
            x = x[0]
        return tuple([s(xi) for xi in x])
    return Statistic(foreach, dim=0, name=f'applies {s.name} to every component of input value')


# #
# # ATTN: Need better handling of dim, arity, codim.  arity=0, etc. is fine while dim is the minimum dimension allowed
# # codim=0 means returns a tuple whose equals its input length; codim=n means returns an n-tuple, codim=None is unknown
# #
def Fork(stat: Statistic, *more_stats: Statistic) -> Statistic:
    # Arities must all be the same
    if any([s.arity != stat.arity for s in more_stats]):  #ATTN!: Statistics need to distinguish arity from minimum dim, need two properties
        raise ValueError('Fork must be called on statistics with the same dimension')
    codim = 0
    if stat.codim is not None and stat.codim > 0 and all([s.codim is not None and s.codim > 0 for s in more_stats]):
        codim = stat.codim + sum(s.codim for s in more_stats)  # type: ignore
    def forked(*x):
        returns = list(stat(x))
        for s in more_stats:
            returns.extend(s(x))
        return returns
    return Statistic(forked, dim=stat.arity, codim=codim, name=f'fork({stat.name}, {", ".join([s.name for s in more_stats])})')

## ATTN: Add 
# Permute    ATTN: fix up but keeping it simple for now
def Permute(p: Iterable[int]):
    # assert p contains all unique values from 1..n
    perm = list(map(lambda k: k - 1, p))
    n = len(perm)
    @statistic(name=f'Permutation', dim=0)   # ATTN
    def permute(value):
        return VecTuple(value[perm[i]] for i in range(n))
    return permute
        


def IfThenElse( cond: Statistic
              , t: Statistic | tuple | float | int
              , f: Statistic | tuple | float | int
              ) -> Statistic:
    if not is_statistic(t):
        t = Constantly(t)
    if not is_statistic(f):
        f = Constantly(f)
    # ATTN: arity conditions need to be more nuanced
    #if cond.arity != t.arity or t.arity != f.arity or t.codim != f.codim:
    if t.codim is not None and f.codim is not None and t.codim != f.codim:
        raise ValueError(f'True and False statistics for IfElse must have matching dim and codim')  # ATTN:Replace with custom error for catching at repl
    def ifelse(*x):
        if cond(*x):
            return t(*x)
        else:
            return f(*x)
    return Statistic(ifelse, dim=cond.arity, codim=t.codim, name=f'returns {t.name} if {cond.name} is true else returns {f.name}')
        
def Not(s: Statistic) -> Condition:
    #ATTN: require s.codim == 1
    return Condition(lambda *x: 1 - s(*x), dim=s.arity, name=f'not({s.name})', description=f'returns the logical not of {s.name}')

# def And(s1: Statistic, s2: Statistic) -> Statistic:
#     #ATTN: require si.codim == 1 and s1.arity == s2.arity
#     return Statistic(lambda *x: s1(*x) and s2(*x), dim=s1.arity, codim=1, name=f'Logical And of {s1.name} and {s2.name}')
#  
# def Or(s1: Statistic, s2: Statistic) -> Statistic:
#     #ATTN: require si.codim == 1 and s1.arity == s2.arity
#     return Statistic(lambda *x: s1(*x) or s2(*x), dim=s1.arity, codim=1, name=f'Logical Or of {s1.name} and {s2.name}')

def And(*stats: Statistic) -> Condition:
    #ATTN: require si.codim == 1 and s1.arity == s2.arity
    def and_of(*x):
        val = True
        for s in stats:
            val = val and s(*x)
            if not val:
                break
        return val
    labels = ["'" + s.name + "'" for s in stats]
    return Condition(and_of, dim=max(s.arity for s in stats), name=f'({" and ".join(labels)})', description=f'returns the logical and of {", ".join(labels)}')

def Or(*stats: Statistic) -> Condition:
    #ATTN: require si.codim == 1 and s1.arity == s2.arity
    def and_of(*x):
        val = False
        for s in stats:
            val = val or s(*x)
            if val:
                break
        return val
    labels = ["'" + s.name + "'" for s in stats]
    return Condition(and_of, dim=max(s.arity for s in stats), name=f'({" or ".join(labels)})', description=f'returns the logical or of {", ".join(labels)}')

top = Condition(lambda _x: True, name='top', description='returns true for any value')

bottom = Condition(lambda _x: False, name='bottom', description='returns false for any value')


## ATTN: These should really be methods of ProjectionStatistic
## There should be no need for a callable argment in that constructor.
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

    # ATTN:Support slice objects here
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

