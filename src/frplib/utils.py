from __future__ import annotations

import sys

from collections.abc   import Iterable
from functools         import reduce
from typing            import Callable, Generator, TypeVar
from typing_extensions import Any, TypeGuard

from frplib.env        import environment
from frplib.exceptions import ConstructionError, OperationError
#
# Generic
#

A = TypeVar('A')

def identity(x: A) -> A:
    "Returns its argument."
    return x

def const(a: A) -> Callable[[Any], A]:
    "Returns a constant function that returns the given value."
    def const_fn(x: Any) -> A:
        return a
    return const_fn


#
# Kinds and FRPs and Such
#

def values(x, scalarize=False) -> set:
    """Returns the set of values of a kind.

    Parameters:
    ----------
      x - a kind, or any object with a .values property
      scalarize [False] - if True, convert numeric scalars to floats

    Returns a set of possible values, with scalars unwrapped from
    their tuples.

    """
    try:
        if scalarize:
            return set(map(float, x.values))
        return x.values
    except Exception:
        raise OperationError(f'Object {str(x)} does not have a values property.')

def dim(x):
    "Returns the dimension of its argument, which is typically a kind, FRP, or statistic."
    try:
        return x.dim
    except Exception:
        raise OperationError(f'Object {str(x)} does not have a dim property.')

def codim(x):
    "Returns the co-dimension of its argument, which is typically a kind, FRP, or statistic."
    try:
        return x.codim
    except Exception:
        raise OperationError(f'Object {str(x)} does not have a codim property.')

def size(x):
    "Returns the size of its argument, which is typically a kind or FRP."
    try:
        return x.size
    except Exception:
        raise OperationError(f'Object {str(x)} does not have a size property.')

def clone(x):
    """Returns a clone of its argument, which is typically an FRP or conditional FRP.

    This operates on any object with a .clone() method, but is typically used
    to get a copy of an FRP or conditional FRP with the same kind but its
    own value.

    """
    try:
        return x.clone()
    except Exception as e:
        raise OperationError(f'Could not clone object {x}: {str(e)}')


#
# Tuples
#

def is_tuple(x: Any) -> TypeGuard[tuple]:
    "Is the given object a tuple?"
    return isinstance(x, tuple)

def scalarize(x):
    "If given a length 1 tuple, unwrap the value; otherwise returns argument as is."
    return (x[0] if isinstance(x, tuple) and len(x) == 1 else x)

def ensure_tuple(x: Any) -> tuple:
    "If given a non-tuple, wrap in a length 1 tuple; else returns argument as is."
    return (x if isinstance(x, tuple) else (x,))


#
# Sequences and Collections
#

def irange(
        start_or_stop: int,
        stop: int | None = None,
        *,
        step=1,
        exclude: Callable[[int], bool] | Iterable[int] | None = None,
        include: Callable[[int], bool] | Iterable[int] | None = None,
) -> Generator[int, None, None]:
    """Inclusive integer range.

    Parameters
    ----------
      start_or_stop - if the only argument, an integer giving the stop (inclusive)
          of the sequence; if stop is also supplied, this is the start.
      stop - if missing, start from 1 (unlike the builtin range that starts from 0);
          otherwise, the sequence goes up to and including this value.
      step - a non-zero integer giving the spacing between successive values of the
          sequence; it can e negativ if stop < start.
      exclude - either a set of integers or a predicate taking integers to boolean
          values; values in the set or for which the predicate returns true are skippe.
      include - either a set of integers or a predicate taking integers to boolean
          values; values in the set or for which the predicate returns true are included.
          If exclude is also supplied, this takes precedence.

    Returns an iterator over the resulting range.

    """
    if exclude is not None and not callable(exclude):
        exclude_values = set(exclude)
        exclude = lambda x: x in exclude_values
    if include is not None and not callable(include):
        include_values = set(include)
        include = lambda x: x in include_values

    if stop is None:
        stop = start_or_stop
        start = 1
    else:
        start = start_or_stop

    if (stop - start) * step <= 0:
        raise ConstructionError(f'irange {start}:{stop} and step {step} have inconsistent direction.')

    sign = 1 if step >= 0 else -1

    def generate_from_irange() -> Generator[int, None, None]:
        value = start
        while (value - stop) * sign <= 0:
            if ((include is None and exclude is None) or
               (include is not None and include(value)) or
               (exclude is not None and not exclude(value))):
                yield value
            value += step

    return generate_from_irange()

def index_of(value, xs, not_found=-1, *, start=0, stop=sys.maxsize):
    """Returns index of `value` in `xs`, or `not_found` if none.

    If xs is a list or tuple, restrict attention to the slice
    from start to stop, exclusive, where start <= stop.

    """
    if stop <= start:
        return not_found

    if isinstance(xs, (list, tuple)):
        try:
            return xs.index(value, start, stop)
        except ValueError:
            return not_found
    else:
        for i, v in enumerate(xs):
            if i >= start and i < stop and v == value:
                return i
        return not_found


#
# Higher-Order Functions
#

def compose(*functions):
    """Returns a new function that composes the given functions successively.

    Note that compose(f,g) calls f *after* g. The values of g should be
    valid inputs to f, and similarly for any list of functions.
    This is not checked, however.

    """
    def compose2(f, g):
        return lambda x: f(g(x))

    n = len(functions)
    if n == 0:
        return identity

    if n == 1:
        return functions[0]

    if n == 2:
        return compose2(functions[0], functions[1])

    return reduce(compose2, functions)

    #  # For later Python versions
    # match functions:
    #     case ():
    #         return identity
    #     case (f,):
    #         return f
    #     case (f, g):
    #         return compose2(f, g)
    #     case _:
    #         return reduce(compose2, functions )

def lmap(func, *iterables):
    "Like the builtin `map` but automatically converts its results into a list."
    return list(map(func, *iterables))

def every(func, iterable):
    "Returns true if f(x) is truthy for every x in iterable."
    return all(map(func, iterable))

def some(func, iterable):
    "Returns true if f(x) is truthy for some x in iterable."
    return any(map(func, iterable))


#
# Environment
#

def is_interactive() -> bool:
    "Checks if frp is running as an interactive app."
    return environment.is_interactive or hasattr(sys, 'ps1') or bool(sys.flags.interactive)
