from __future__ import annotations

#
# vec_tuples.py - vector-like tuples with extension/broadcasting rules
#
# These are like regular python tuples except that arithmetic
# and comparison operations act componentwise like vectors.
# Additional operations like dot product and modulus are
# also supported and produce scalar (1-dim) vectors.
#
# Note that comparisons are in a mathematical-style partial order
# with all-like semantics. To get the ordinary tuple dictionary
# ordering, need to apply tuple().
#
# When vectors of differing dimension are combined, the
# shorter one is extended by one of three extension rules:
#
#   + Scalar extension: scalars are extended, error otherwise
#   + Zero extension: scalars are extended by repetition, others
#     with 0s appended, embedding them in the larger space.
#   + Cyclic extension: cycling repetition as in R
#
# Some extension is needed for promoting scalar operations
# conveniently, but which to use is not yet clear.
# R-style cyclic extension (cyclic_extend) can be convenient
# for expressing some statistics but seems likely to obscure
# potential errors. Zero extension (zero_extend) makes
# sense in terms of the embedding of low dimensional into high
# dimensional and might be convenient to avoid repetition,
# but it treats scalars differently and again can obscure
# intentions. Scalar extension (scalar_extend) is conservative,
# slightly less functional but prevents needless mistakes.
#
# Currently, this module implements Scalar extension.
#

import math

from collections.abc   import Iterable
from decimal           import Decimal
from fractions         import Fraction
from functools         import reduce
from operator          import (add, mul, sub, truediv, floordiv, mod, pow,
                               lt, gt, eq, le, ge)
from typing            import cast, Type, TypeVar, Union
from typing_extensions import Self, TypeGuard

from frplib.exceptions import (OperationError, NumericConversionError,
                               MismatchedDimensionError, MismatchedDomain)
from frplib.numeric    import Numeric, NumericF, NumericD, NumericB, numeric_sqrt  # ATTN: Numeric+Symbolic+SupportsVec
from frplib.numeric    import as_numeric as scalar_as_numeric
from frplib.symbolic   import Symbolic, symbolic_sqrt

# SupportsVec  mixin can allow Symbolic and VecTuple automatically,   __plus__  __scalar_mul__
# SupportsNumeric protocol __numeric__ with numeric conversion.
# Can newtype Decimal and Fraction etc.; subclass with __slots__

#
# Types
#

# A VecTuple should contain entirely interoperable types
T = TypeVar('T', NumericF, NumericD, NumericB, Union[Numeric, Symbolic])


#
# R-style cyclic extension of shorter vectors to longer length
#

def extend_list_cyclically(v: list, v_len: int, longer_len: int) -> list:
    "Extend list to a *strictly longer* length by R-style cycling repetition."
    reps = longer_len // v_len
    extra = longer_len % v_len

    extended = v * reps
    if extra > 0:  # Note: R issues warning in this case
        extended.extend(v[:extra])
    return extended

def cyclic_extend(
        vec: VecTuple[T],
        other: Union[T, Iterable[T]]
) -> tuple[VecTuple[T], VecTuple[T]]:
    """Stretches two vectors to the longer length by cycling extension.

    Parameters:
      vec - a VecTuple
      other - a scalar or other iterable, iterator/generator allowed

    Returns a pair of VecTuples in the same order where the shorter
    of vec and other is extended to the length of the longer
    by R-style cycling extension.

    """
    n = len(vec)
    # Optimize for most common cases
    if isinstance(other, VecTuple) and len(other) == n:
        return (vec, other)
    if isinstance(other, (int, float, Fraction, Decimal, Symbolic)):
        return (vec, VecTuple([other] * n))

    # We'll likely need a list for other but also handles iterators
    try:
        y = list(other)
    except Exception:
        raise OperationError('Object cannot be converted to a VecTuple.')
    m = len(y)

    if m == n:
        return (vec, VecTuple(y))

    if m < n:
        return (vec, VecTuple(extend_list_cyclically(y, m, n)))

    return (VecTuple(extend_list_cyclically(list(vec), n, m)), VecTuple(y))

#
# Zero extension: extend non-scalar vectors by 0 to the longer length
#     Scalars are extended by repetition to promote scalar operaitons.
#

def zero_extend(
        vec: VecTuple[T],
        other: Union[T, Iterable[T]]
) -> tuple[VecTuple[T], VecTuple[T]]:
    """Stretches to vectors to the same length by cycling extension.

    Parameters:
      vec - a VecTuple
      other - a scalar or other iterable, iterator/generator allowed

    Returns a pair of VecTuples in the same order where the shorter
    of vec and other is extended to the length of the longer
    by R-style cycling extension.

    """
    n = len(vec)
    # Optimize for most common cases
    if isinstance(other, VecTuple) and (len(other) == n or len(other) == 1):
        if len(other) == n:
            return (vec, other)
        return (vec, VecTuple(list(other) * n))
    if isinstance(other, (int, float, Fraction, Decimal, Symbolic)):
        return (vec, VecTuple([other] * n))

    # We'll likely need a list for other but also handles iterators
    try:
        y = list(other)
    except Exception:
        raise OperationError('Object cannot be converted to a VecTuple.')
    m = len(y)

    if m == n:
        return (vec, VecTuple(y))

    if m < n:
        return (vec, VecTuple(y + [0] * (m - n)))

    return (VecTuple(list(vec) + [0] * (n - m)), VecTuple(y))


#
# Scalar extension: extend scalars but raise MismatchedDimensionError otherwise
#

def scalar_extend(
        vec: VecTuple[T],
        other: Union[T, Iterable[T]]
) -> tuple[VecTuple[T], VecTuple[T]]:
    """Stretches to vectors to the same length by cycling extension.

    Parameters:
      vec - a VecTuple
      other - a scalar or other iterable, iterator/generator allowed

    Returns a pair of VecTuples in the same order where the shorter
    of vec and other is extended to the length of the longer
    by R-style cycling extension.

    """
    n = len(vec)
    # Optimize for most common cases
    if isinstance(other, VecTuple) and (len(other) == n or len(other) == 1):
        if len(other) == n:
            return (vec, other)
        return (vec, VecTuple(list(other) * n))
    if isinstance(other, (int, float, Fraction, Decimal, Symbolic)):
        return (vec, VecTuple([other] * n))

    # We'll likely need a list for other but also handles iterators
    try:
        y = list(other)
    except Exception:
        raise OperationError('Object cannot be converted to a VecTuple.')

    m = len(y)
    if m == n:
        return (vec, VecTuple(y))
    if m == 1:
        return (vec, VecTuple(y * n))
    if n == 1:
        return (VecTuple(list(vec) * m), VecTuple(y))

    raise MismatchedDimensionError(f'Invalid attempt to operate on vec tuples '
                                   f'of incompatible dimensions {n} and {m}')


#
# Extended operations using the chosen extension style
#

def extended_op(op, left, right):
    "VecTuple operation with extension where left operand is known to be a VecTuple."
    try:
        x, y = scalar_extend(left, right)
    except OperationError:
        return NotImplemented
    return VecTuple(map(op, x, y))

def extended_rop(op, left, right):
    "VecTuple operation with extension where right operand is known to be a VecTuple."
    try:
        y, x = scalar_extend(right, left)
    except OperationError:
        return NotImplemented
    return VecTuple(map(op, x, y))

def extended_all_cmp(cmp, left, right):
    "VecTuple comparison with extension and all-semantics; left is a VecTuple."
    # Catch errors above
    x, y = scalar_extend(left, right)
    return all(cmp(xi, yi) for xi, yi in zip(x, y))

def extended_some_cmp(cmp, left, right):
    "VecTuple comparison with extension and some-semantics; left is a VecTuple."
    # Catch errors above
    x, y = scalar_extend(left, right)
    return any(cmp(xi, yi) for xi, yi in zip(x, y))


#
# Helpers
#

def dot_product(a: VecTuple[T], b_star: Iterable[T]) -> T:
    b = list(b_star)
    if len(b) != len(a):
        raise OperationError('VecTuple dot product requires tuples of equal dimension')
    return reduce(add, map(mul, a, b), cast(T, 0))

def from_scalar(x):
    # Want T here but allow Quantity here when available
    if isinstance(x, (int, float, Fraction, Decimal, Symbolic)):
        return VecTuple([x])
    return x

def as_scalar(x) -> T | None:
    if isinstance(x, (int, float, Fraction, Decimal, Symbolic, bool)):
        return cast(T, x)
    elif isinstance(x, tuple) and len(x) == 1:
        return cast(T, x[0])
    return None

def as_scalar_strict(x) -> T:
    if isinstance(x, (int, float, Fraction, Decimal, Symbolic, str, bool)):
        return cast(T, x)
    elif isinstance(x, tuple) and len(x) == 1:
        return cast(T, x[0])
    raise NumericConversionError(f'The quantity {x} could not be converted to a numeric/symbolic scalar.')

def as_scalar_weak(x):
    "Returns a scalar if convertible, otherwise bail and return the argument."
    if isinstance(x, (int, float, Fraction, Decimal, Symbolic, bool)):
        return x
    elif isinstance(x, tuple) and len(x) == 1:
        return x[0]
    return x


#
# Numeric/Quantified VecTuples
#

class VecTuple(tuple[T, ...]):
    "A variant tuple type that supports addition and scalar multiplication like a vector."
    def __new__(cls, contents: Iterable[T]) -> 'VecTuple[T]':
        return super().__new__(cls, contents)     # type: ignore

    def __str__(self):
        return f'<{", ".join(map(str, self))}>'

    def __frplib_repr__(self):
        return self.__str__()

    def map(self, fn) -> 'VecTuple[T]':
        return self.__class__(map(fn, self))

    @property
    def dim(self):
        return len(self)

    @classmethod
    def show(cls, vtuple: 'VecTuple[T]', scalarize=True) -> str:
        if scalarize and len(vtuple) == 1:
            return str(vtuple[0])
        return str(vtuple)

    def __add__(self, other) -> 'VecTuple[T]':
        return extended_op(add, self, other)

    def __radd__(self, other) -> 'VecTuple[T]':
        return extended_rop(add, other, self)

    def __sub__(self, other) -> 'VecTuple[T]':
        return extended_op(sub, self, other)

    def __rsub__(self, other) -> 'VecTuple[T]':
        return extended_rop(sub, other, self)

    def __mul__(self, other) -> 'VecTuple[T]':
        return extended_op(mul, self, other)

    def __rmul__(self, other) -> 'VecTuple[T]':
        return extended_rop(mul, other, self)

    def __truediv__(self, other) -> 'VecTuple[T]':
        return extended_op(truediv, self, other)

    def __rtruediv__(self, other) -> 'VecTuple[T]':
        return extended_rop(truediv, other, self)

    def __floordiv__(self, other) -> 'VecTuple[T]':
        return extended_op(floordiv, self, other)

    def __rfloordiv__(self, other) -> 'VecTuple[T]':
        return extended_rop(floordiv, other, self)

    def __mod__(self, other) -> 'VecTuple[T]':
        return extended_op(mod, self, other)

    def __rmod__(self, other) -> 'VecTuple[T]':
        return extended_rop(mod, other, self)

    def __pow__(self, other) -> 'VecTuple[T]':
        return extended_op(pow, self, other)

    def __rpow__(self, other) -> 'VecTuple[T]':
        return extended_rop(pow, other, self)

    def __matmul__(self, other) -> VecTuple[T]:
        if not isinstance(other, Iterable):  # Allow vector like things
            return NotImplemented
        return vec_tuple(dot_product(self, other))

    def __abs__(self):
        sq_norm = dot_product(self, self)
        if isinstance(sq_norm, Symbolic):
            raise NotImplementedError('Symbolic function application not yet implemented')
        dot_prod = dot_product(self, self)
        if isinstance(dot_prod, Symbolic):
            return vec_tuple(symbolic_sqrt(dot_prod))
        elif isinstance(dot_prod, (int, Decimal)):
            return vec_tuple(numeric_sqrt(dot_prod))
        return vec_tuple(math.sqrt(dot_prod))

    def __getitem__(self, key):
        x = super().__getitem__(key)
        if isinstance(key, slice):
            return VecTuple(x)
        return x

    def __eq__(self, other):
        try:
            return extended_all_cmp(eq, self, other)
        except (OperationError, MismatchedDimensionError):
            return False
        except TypeError as e:
            raise OperationError(f'Could not test for == with {other}: {str(e)}')
        # other = from_scalar(other)   # Allow scalar equality of VecTuples, no invariants changed
        # try:
        #     return super().__eq__(other)
        # except TypeError as e:
        #     raise OperationError(f'Could not test for == with {other}: {str(e)}')

    def __hash__(self):  # Need this because we play with __eq__
        return super().__hash__()  # Modified __eq__ does not change the invariant

    def __ne__(self, other):
        try:
            return not extended_all_cmp(eq, self, other)  # *any* ne means True
        except (OperationError, MismatchedDimensionError):
            return True
        except TypeError as e:
            raise OperationError(f'Could not test for != with {other}: {str(e)}')
        # other = from_scalar(other)   # Allow scalar comparison of VecTuples
        # try:
        #     return super().__ne__(other)
        # except TypeError as e:
        #     raise OperationError(f'Could not test for != with {other}: {str(e)}')

    def __lt__(self, other):
        try:
            return extended_all_cmp(le, self, other) and extended_some_cmp(lt, self, other)
        except TypeError as e:
            raise OperationError(f'Could not test for < with {other}: {str(e)}')
        # other = from_scalar(other)   # Allow scalar comparison of VecTuples
        # try:
        #     return super().__lt__(other)
        # except TypeError as e:
        #     raise OperationError(f'Could not test for != with {other}: {str(e)}')

    def __le__(self, other):
        try:
            return extended_all_cmp(le, self, other)
        except TypeError as e:
            raise OperationError(f'Could not test for <= with {other}: {str(e)}')
        # other = from_scalar(other)   # Allow scalar comparison of VecTuples
        # try:
        #     return super().__le__(other)
        # except TypeError as e:
        #     raise OperationError(f'Could not test for != with {other}: {str(e)}')

    def __gt__(self, other):
        try:
            return extended_all_cmp(ge, self, other) and extended_some_cmp(gt, self, other)
        except TypeError as e:
            raise OperationError(f'Could not test for > with {other}: {str(e)}')
        # other = from_scalar(other)   # Allow scalar comparison of VecTuples
        # try:
        #     return super().__gt__(other)
        # except TypeError as e:
        #     raise OperationError(f'Could not test for != with {other}: {str(e)}')

    def __ge__(self, other):
        try:
            return extended_all_cmp(ge, self, other)
        except TypeError as e:
            raise OperationError(f'Could not test for >= with {other}: {str(e)}')
        # other = from_scalar(other)   # Allow scalar comparison of VecTuples
        # try:
        #     return super().__ge__(other)
        # except TypeError as e:
        #     raise OperationError(f'Could not test for != with {other}: {str(e)}')

    @classmethod
    def join(cls: Type[Self], values: Iterable[Self]) -> Self:
        combined = []
        for value in values:
            combined.extend(list(value))
        return cls(combined)

    @classmethod
    def concat(cls: Type[Self], *values: Self) -> Self:
        return cls.join(values)


def vec_tuple(*a: T) -> VecTuple[T]:
    "Collects its arguments into a VecTuple"
    return VecTuple(a)

def as_vec_tuple(x: T | Iterable[T] = ()) -> VecTuple[T]:
    "Converts an iterable to (or wraps a single value in) a VecTuple"
    if isinstance(x, VecTuple):
        return x
    if isinstance(x, Iterable) and not isinstance(x, str):
        return VecTuple(x)
    return vec_tuple(x)

def as_numeric_vec(x):
    # ATTN: Consider using as_real here
    if isinstance(x, Iterable) and not isinstance(x, str):
        return VecTuple(map(scalar_as_numeric, x))
    else:
        return vec_tuple(scalar_as_numeric(x))

def is_vec_tuple(x) -> TypeGuard[VecTuple[T]]:
    "Is this a VecTuple?"
    return isinstance(x, VecTuple)

def value_set(*vals) -> set[VecTuple]:
    """Create a set of VecTuples from specified values or a single iterator.

    Requires all values to have the *same dimension* or an error is raised.
    If only one value is supplied that is an iterator or generator,
    that is used as the source of values. See also `value_set_from`.

    Returns a set of values.

    """
    if len(vals) == 1 and hasattr(vals[0], '__next__'):
        # We have been given a single iterator/generator, use it
        vals = vals[0]
    vs = set([as_vec_tuple(v) for v in vals])
    dims = set(map(len, vs))
    if len(dims) != 1:
        raise MismatchedDomain(f'Value set elements have different dimensions, {dims}.')
    return vs

def value_set_from(vals: Iterable) -> set[VecTuple]:
    """Create a set of VecTuples from an iterable object.

    Requires all values to have the *same dimension* or an error is raised.
    See also `value_set`.

    Returns a set of values.

    """
    vs = set([as_vec_tuple(v) for v in vals])
    dims = set(map(len, vs))
    if len(dims) != 1:
        raise MismatchedDomain(f'Value set elements have different dimensions, {dims}.')
    return vs
