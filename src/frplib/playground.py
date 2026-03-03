"""Convenience module mirroring the FRP Playground namespace for stand-alone use.

Exports all symbols available in the interactive playground, so that one
can do

    from frplib.playground import *

without needing many explicit imports. This is convenient for frplib scripts
and for recording transcripts of playground sessions. For extended code,
we recommend using explicit imports.

Note that this shadows the Python built-in ``bin`` in the importing
namespace, which is intentional and matches playground behaviour.
The names ``And``, ``Or``, ``Not``, ``Any``, and ``All`` are
capitalised frplib statistics and are intentionally reminiscent of
their Python counterparts, but do not shadow them.

"""

from __future__ import annotations

from decimal import Decimal

from frplib.kinds import (                                # pylint: disable=redefined-builtin
    Kind, ConditionalKind,
    kind, conditional_kind,
    is_kind, unfold, clean, fast_mixture_pow, bayes,
    constant, uniform, either, binary,
    symmetric, linear, geometric,
    weighted_by, weighted_as, weighted_pairs,
    arbitrary, integers, evenly_spaced, bin,
    without_replacement, ordered_samples, subsets, permutations_of,
)

from frplib.statistics import (
    Statistic, Condition, MonoidalStatistic,
    is_statistic, statistic, condition, scalar_statistic,
    tuple_safe, infinity, is_true, is_false,
    Chain, Compose, scalar_fn,
    Id, Scalar, __, Proj, _x_,
    Sum, Product, Count, Max, Min, Abs, SumSq,
    Sqrt, Floor, Ceil, NormalCDF, Binomial,
    Exp, Log, Log2, Log10,
    Sin, Cos, Tan, ACos, ASin, ATan2, Sinh, Cosh, Tanh,
    Pi, FromDegrees, FromRadians,
    Mean, StdDev, Variance,
    Median, Quartiles, IQR,
    Norm, Dot,
    ArgMin, ArgMax, Ascending, Descending, Distinct,
    Diff, Diffs, Permute, ElementOf,
    Constantly, Fork, MFork, ForEach, IfThenElse,
    And, Or, Not, Xor, top, bottom,
    All, Any, Cases, Bag, Append, Prepend,
    Get, Keep, MaybeMap,
    Freqs, IndexOf, Contains,
)

from frplib.expectations import E, Var, D_

from frplib.frps import (
    FRP, frp, conditional_frp, is_frp, evolve,
    average_conditional_entropy, mutual_information, shuffle,
)

from frplib.calculate import substitute, substitute_with, substitution

from frplib.numeric import (
    numeric_exp, numeric_ln, numeric_log10, numeric_log2,
    numeric_abs, numeric_sqrt, numeric_floor, numeric_ceil,
    nothing,
)

from frplib.quantity import as_quantity, qvec

from frplib.symbolic import gen_symbol, is_symbolic, is_zero, symbol, symbols

from frplib.utils import (
    clone, compose, const, every, frequencies,
    identity, index_of, index_where, irange, iterate, iterates,
    lmap, fold, fold1,
    values, dim, codim, size, typeof, show, some,
)

from frplib.vec_tuples import (
    VecTuple,
    as_numeric_vec, as_scalar, as_vec_tuple, as_float, as_bool,
    is_vec_tuple, vec_tuple, join,
)

from frplib.market import Market

from frplib.extras import components


__all__ = [
    # decimal
    'Decimal',
    # frplib.kinds
    'Kind', 'ConditionalKind',
    'kind', 'conditional_kind',
    'is_kind', 'unfold', 'clean', 'fast_mixture_pow', 'bayes',
    'constant', 'uniform', 'either', 'binary',
    'symmetric', 'linear', 'geometric',
    'weighted_by', 'weighted_as', 'weighted_pairs',
    'arbitrary', 'integers', 'evenly_spaced', 'bin',
    'without_replacement', 'ordered_samples', 'subsets', 'permutations_of',
    # frplib.statistics
    'Statistic', 'Condition', 'MonoidalStatistic',
    'is_statistic', 'statistic', 'condition', 'scalar_statistic',
    'tuple_safe', 'infinity', 'is_true', 'is_false',
    'Chain', 'Compose', 'scalar_fn',
    'Id', 'Scalar', '__', 'Proj', '_x_',
    'Sum', 'Product', 'Count', 'Max', 'Min', 'Abs', 'SumSq',
    'Sqrt', 'Floor', 'Ceil', 'NormalCDF', 'Binomial',
    'Exp', 'Log', 'Log2', 'Log10',
    'Sin', 'Cos', 'Tan', 'ACos', 'ASin', 'ATan2', 'Sinh', 'Cosh', 'Tanh',
    'Pi', 'FromDegrees', 'FromRadians',
    'Mean', 'StdDev', 'Variance',
    'Median', 'Quartiles', 'IQR',
    'Norm', 'Dot',
    'ArgMin', 'ArgMax', 'Ascending', 'Descending', 'Distinct',
    'Diff', 'Diffs', 'Permute', 'ElementOf',
    'Constantly', 'Fork', 'MFork', 'ForEach', 'IfThenElse',
    'And', 'Or', 'Not', 'Xor', 'top', 'bottom',
    'All', 'Any', 'Cases', 'Bag', 'Append', 'Prepend',
    'Get', 'Keep', 'MaybeMap',
    'Freqs', 'IndexOf', 'Contains',
    # frplib.expectations
    'E', 'Var', 'D_',
    # frplib.frps
    'FRP', 'frp', 'conditional_frp', 'is_frp', 'evolve',
    'average_conditional_entropy', 'mutual_information', 'shuffle',
    # frplib.calculate
    'substitute', 'substitute_with', 'substitution',
    # frplib.numeric
    'numeric_exp', 'numeric_ln', 'numeric_log10', 'numeric_log2',
    'numeric_abs', 'numeric_sqrt', 'numeric_floor', 'numeric_ceil',
    'nothing',
    # frplib.quantity
    'as_quantity', 'qvec',
    # frplib.symbolic
    'gen_symbol', 'is_symbolic', 'is_zero', 'symbol', 'symbols',
    # frplib.utils
    'clone', 'compose', 'const', 'every', 'frequencies',
    'identity', 'index_of', 'index_where', 'irange', 'iterate', 'iterates',
    'lmap', 'fold', 'fold1',
    'values', 'dim', 'codim', 'size', 'typeof', 'show', 'some',
    # frplib.vec_tuples
    'VecTuple',
    'as_numeric_vec', 'as_scalar', 'as_vec_tuple', 'as_float', 'as_bool',
    'is_vec_tuple', 'vec_tuple', 'join',
    # frplib.market
    'Market',
    # frplib.extras
    'components',
]
