from __future__ import annotations

import math
import random
import re

from collections.abc   import Collection, Iterable
from dataclasses       import dataclass
from enum              import Enum, auto
from itertools         import chain, combinations, permutations, product, starmap
from typing            import Literal, Callable, overload, Union, cast
from typing_extensions import Any, TypeAlias, TypeGuard


from rich              import box
from rich.panel        import Panel

from frplib.env        import environment
from frplib.exceptions import (ConstructionError, EvaluationError, KindError, MismatchedDomain,
                               OperationError)
from frplib.kind_trees import (KindBranch,
                               canonical_from_sexp, canonical_from_tree,
                               unfold_tree, unfolded_labels, unfold_scan, unfolded_str)
from frplib.numeric    import (Numeric, ScalarQ, as_nice_numeric, as_numeric, as_real,
                               is_numeric, numeric_abs, numeric_floor, numeric_log2, numeric_ln)
from frplib.output     import RichReal, RichString
from frplib.protocols  import Projection, SupportsKindOf
from frplib.quantity   import as_quantity, as_nice_quantity, as_quant_vec, show_quantities, show_qtuples
from frplib.statistics import Condition, MonoidalStatistic, Statistic, compose2, Proj
from frplib.symbolic   import Symbolic, gen_symbol, is_symbolic, symbol
from frplib.utils      import compose, const, dim, identity, is_interactive, is_tuple, lmap
from frplib.vec_tuples import (VecTuple, as_numeric_vec, as_scalar_strict, as_vec_tuple, vec_tuple,
                               as_scalar_weak, value_set_from)


#
# Types (ATTN)
#

CanonicalKind: TypeAlias = list['KindBranch']
QuantityType: TypeAlias = Union[Numeric, Symbolic]
ValueType: TypeAlias = VecTuple[QuantityType]  # ATTN


#
# Constants
#


#
# Helpers
#

def dict_as_value_map(d: dict, values: set | None = None) -> Callable:
    """Converts a dictionary keyed by values into a function that accepts values.

    The keys in the dictionary can be scalars or regular tuples for convenience,
    but the function always accepts vec_tuples only.

    If `values` is a supplied, it should be a set specifying the domain.
    In this case, the input dictionary `d` is checked that it has a
    value for each possible input.

    In any case, all the values in `d` should have the same dimension
    whether they be Kinds, Statistics, conditional Kinds, VecTuples,
    or even conditional FRPs.  The latter case can lead to excess computation
    if the FRP is lazy and so should be avoided.

    Returns a function on the specified domain.

    """
    if values is not None:
        d_keys = {as_vec_tuple(vs) for vs in d.keys()}
        if d_keys < values:   # superset of values is ok
            raise KindError('All specified values must be present to convert a dictionary to a value function.\n'
                            'This likely occurred when creating a conditional Kind to take a mixture.')

        value_dims = {k.dim for k in d.values()}
        if len(value_dims) != 1:
            raise KindError('When converting a dictionary to a value function, all values must '
                            'map to a quantity of the same dimension. This likely occurred when '
                            'creating a conditional Kind to take a mixture.')
    scalar_keys = [vs for vs in d.keys() if not is_tuple(vs) and (vs,) not in d]
    if len(scalar_keys) > 0:
        d = d | {vec_tuple(vs): d[vs] for vs in scalar_keys}

    def d_mapping(*vs):
        if len(vs) == 1 and is_tuple(vs[0]):
            return d[vs[0]]
        return d[vs]

    return d_mapping

# ATTN: this should probably become static methods; see Conditional Kinds.
def value_map(f, kind=None):  # ATTN: make in coming maps tuple safe; add dimension hint even if no kind
    # We require that all kinds returned by f are the same dimension
    # But do not check if None is passed explicitly for kind
    if callable(f):
        # ATTN: second clause requires a conditional Kind; this is fragile
        if kind is not None:
            dim_image = set([f(as_vec_tuple(vs)).dim for vs in kind.value_set])
            if len(dim_image) != 1:
                raise KindError('All values for a transform or mixture must be '
                                'associated with a Kind of the same dimension')
        return f
    elif isinstance(f, dict):
        # ATTN?? Use dict_as_value_map(f, kind.value_set) here instead of the following code
        if kind is not None:
            overlapping = {as_vec_tuple(vs) for vs in f.keys()} & kind.value_set
            if overlapping < kind.value_set:   # superset of values ok
                raise KindError('All values for the kind must be present in a mixture')
            if len({k.dim for k in f.values()}) != 1:
                raise KindError('All values for a mixture must be associated with a Kind of the same dimension')
        scalars = [vs for vs in f.keys() if not is_tuple(vs) and (vs,) not in f]
        if len(scalars) > 0:  # Keep scalar keys but tuplize them as well
            f = f | {(vs,): f[vs] for vs in scalars}  # Note: not mutating on purpose
        return (lambda vs: f[vs])
    # return None
    # move this error to invokation ATTN
    raise KindError('[red]Invalid value transform or mixture provided[/]: '
                    '[italic]should be function or mapping dictionary[/]')

def normalize_branches(canonical) -> list[KindBranch]:
    seen: dict[tuple, KindBranch] = {}
    # ATTN: refactor to make one pass so canonical can be a general iterable without losing it
    # Store as a list initially?  (We need two passes over the final list regardless regardless.)
    total = as_quantity(sum(map(lambda b: b.p, canonical)), convert_numeric=as_real)
    for branch in canonical:
        if branch.vs in seen:
            seen[branch.vs] = KindBranch.make(vs=branch.vs, p=seen[branch.vs].p + branch.p / total)
        else:
            seen[branch.vs] = KindBranch.make(vs=branch.vs, p=branch.p / total)
    return sorted(seen.values(), key=lambda b: tuple(b.vs))

def new_normalize_branches(canonical) -> list[KindBranch]:
    # NOTE: This allows canonical to be a general iterable
    seen: dict[tuple, QuantityType] = {}
    total: QuantityType = 0
    for branch in canonical:
        if branch.vs in seen:
            seen[branch.vs] = seen[branch.vs] + branch.p
        else:
            seen[branch.vs] = branch.p
        total += branch.p
    total = as_quantity(total, convert_numeric=as_real)

    return sorted((KindBranch.make(vs=value, p=weight / total) for value, weight in seen.items()),  # type: ignore
                  key=lambda b: tuple(b.vs))

def drop_input(codim):
    "A simple projection factory for extracting targets from Conditional Kinds."
    def f(v):
        return v[codim:]
    return f

def scalar_safe(f):
    "Wraps a scalar function so that it can accept scalars or tuples."
    def g(v):
        return f(as_scalar_weak(v))

    return g

def vector_safe(f):
    "Wraps a function taking a single VecTuple so that it can accept more flexible inputs."
    def g(v):
        return f(as_vec_tuple(v))

    return g


#
# Kinds
#

class EmptyKindDescriptor:  # Allows Kind.empty to be a Kind
    def __get__(self, obj, objtype=None):
        return objtype([])

class Kind:
    """
    The Kind of a Fixed Random Payoff

    """
    # str | CanonicalKind[a, ProbType] | KindTree[a, ProbType] | Kind[a, ProbType] -> None
    def __init__(self, spec) -> None:
        # branches: CanonicalKind[ValueType, ProbType]
        if isinstance(spec, Kind):
            branches = spec._canonical   # Shared structure OK, Kinds are immutable
        elif isinstance(spec, str):
            branches = canonical_from_sexp(spec)
        elif len(spec) == 0 or isinstance(spec[0], KindBranch):  # CanonicalKind
            branches = normalize_branches(spec)
        else:  # General KindTree
            branches = canonical_from_tree(spec)

        self._canonical: CanonicalKind = branches
        self._size = len(branches)
        self._dimension = 0 if self._size == 0 else len(branches[0].vs)
        self._value_set: set | None = None

    @property
    def size(self):
        "The size of this Kind."
        return self._size

    @property
    def dim(self):
        "The dimension of this Kind."
        return self._dimension

    @property
    def codim(self):
        "The codimension of this Kind."
        return 0

    @property
    def type(self):
        return f'0 -> {self._dimension}'

    def _set_value_set(self):
        elements = []
        for branch in self._canonical:
            elements.append(branch.vs)
        self._value_set = set(elements)

    @property
    def values(self):
        "A user-facing view of the possible values for this kind, with scalar values shown without tuples."
        if self._value_set is None:
            self._set_value_set()   # ensures ._value_set not None
        if self.dim == 1:
            return {x[0] for x in self._value_set}  # type: ignore
        return self._value_set

    @property
    def value_set(self):
        "The raw set of possible values for this kind"
        if self._value_set is None:
            self._set_value_set()
        return self._value_set

    @property
    def _branches(self):
        return self._canonical.__iter__()

    @property
    def weights(self):
        "A dictionary of a Kind's canonical weights by value. See also the `kernel` method."
        # ATTN: wrap this in a pretty_dict from output.py
        return {b.vs: b.p for b in self._canonical}

    def clone(self):
        "Kinds are immutable, so cloning it just returns itself."
        return self

    # Functorial Methods

    # Note 0: Move to keeping everything as a tuple/VecTuple, show the <> for scalars too, reduce this complexity!
    # Note 1: Remove empty kinds in mixtures
    # Note 2: Can we abstract this into a KindMonad superclass using returns style declaration
    #         Then specialize the types of the superclass to tuple[a,...] and something for probs
    # Note 3: Maybe (following 2) the applicative approach should have single functions at the nodes
    #         rather than tuples (which works), because we can always fork the functions to *produce*
    #         tuples, and then the applicative instance is not dependent on the tuple structure
    # Note 4: We want to allow for other types as the values, like functions or bools or whatever;
    #         having kind monad makes that possible. All clean up to tuple-ify things can happen
    #         *here*.
    # Note 5: Need to allow for synonyms of boolean and 0-1 functions in processing maps versus filterings
    #         so events can be used for both and normal predicates can be used
    # Note 6: Need to work out the proper handling of tuples for these functions. See Statistics object
    #         currently in kind_tests.py.  Add a KindUtilities which defines the constructors, statistics,
    #         and other helpers (fork, join, chain, compose, identity, ...)
    # Note 7: Need to improve initialization and use nicer forms in the utilities below
    # Note 8: Have a displayContext (a default, a current global, and with handlers) that governs
    #         i. how kinds are displayed (full, compact, terse), ii. number system used,
    #         iii. rounding and other details such as whether to reduce probs to lowest form, ...
    #         iv. whether to transform values..... The kind can take a context argument that if not None
    #         overrides the surrounding context in the fields supplied.
    # Note 9: Other things: Add annotations to branches to allow nice modeling. Show event {0,1}
    #         trees as their annotated 1 string if present? Formal linear combinations in expectation when not numeric.
    #         Handling boolean and {0,1} equivalently in predicates (so events are as we describe them later)
    # Note A: Large powers maybe can be handled differently to get better performance; or have a reducing method
    #         when doing things like  d6 ** 10 ^ (Sum / 10 - 5)

    def map(self, f):
        "A functorial transformation of this kind. This is for internal use; use .transform() instead."
        new_kind = lmap(KindBranch.bimap(f), self._canonical)
        return Kind(new_kind)

    def apply(self, fn_kind):  # Kind a -> Kind[a -> b] -> Kind[b]
        "An applicative <*> operation on this kind. (For internal use)"
        def app(branch, fn_branch):
            return [KindBranch.make(vs=f(b), p=branch.p * fn_branch.p) for b in branch.vs for f in fn_branch.vs]
        new_kind = []
        for branch in self._canonical:
            for fn_branch in fn_kind._canonical:
                new_kind.extend(app(branch, fn_branch))
        return Kind(new_kind)

    def bind(self, f):   # self -> (a -> Kind[b, ProbType]) -> Kind[b, ProbType]
        "Monadic bind for this kind. (For internal use)"
        def mix(branch):  # KindBranch[a, ProbType] -> list[KindBranch[b, ProbType]]
            subtree = f(branch.vs)._canonical
            return map(lambda sub_branch: KindBranch.make(vs=sub_branch.vs, p=branch.p * sub_branch.p), subtree)

        new_kind = []
        for branch in self._canonical:
            new_kind.extend(mix(branch))
        return Kind(new_kind)

    def bimap(self, value_fn, weight_fn=identity):
        "A functorial transformation of this kind. This is for internal use; use .transform() instead."
        new_kind = lmap(KindBranch.bimap(value_fn, weight_fn), self._canonical)
        return Kind(new_kind)

    @classmethod
    def unit(cls, value):  # a -> Kind[a, ProbType]
        "Returns the monadic unit for this kind. (For internal use)"
        return Kind([KindBranch.make(as_quant_vec(value), 1)])

    @classmethod
    def compare(cls, kind1: Kind, kind2: Kind, tolerance: ScalarQ = '1e-12') -> str:
        """Compares two kinds and returns a diagnostic message about the differences, if any.

        Parameters:
          kind1, kind2 :: the kinds to compare
          tolerance[='1e-12'] :: numerical tolerance for comparing weights

        Returns a (rich) string that prints nicely at the repl.

        """
        if not isinstance(kind1, Kind) or not isinstance(kind2, Kind):
            raise KindError('Kind.compare requires two arguments that are kinds.')

        tol = as_real(tolerance)

        vals1 = kind1.value_set
        vals2 = kind2.value_set

        if vals1 != vals2:
            return RichString(f'The two kinds [bold red]differ[/]. '
                              f'The first has distinct values [red]{set(map(str, vals1 - vals2))}[/] and '
                              f'the second has distinct values [red]{set(map(str, vals2 - vals1))}[/].')

        w1 = kind1.weights
        w2 = kind2.weights

        for v in vals1:
            if as_nice_numeric(as_real(w1[v] - w2[v]).copy_abs()) >= tol:
                return RichString(f'The two kinds [bold red]differ[/] in their weights, '
                                  f'e.g., at value [bold]{v}[/], the weights are [red]{w1[v]}[/] and [red]{w2[v]}[/].')

        return RichString('The two kinds are the [bold green]same[/] within numerical precision.')

    @classmethod
    def equal(cls, kind1, kind2, tolerance: ScalarQ = '1e-12') -> bool:
        """Compares two kinds and returns True if they are equal within numerical tolerance.

        Parameters:
          kind1, kind2 :: the kinds to compare
          tolerance[='1e-12'] :: numerical tolerance for comparing weights

        Returns True if the kinds are the same (within tolerance), else False.

        """
        if not isinstance(kind1, Kind) or not isinstance(kind2, Kind):
            raise KindError('Kind.equal requires two arguments that are kinds.')

        if kind1.dim != kind2.dim or kind1.size != kind2.size:
            return False

        tol = as_real(tolerance)

        vals1 = kind1.value_set
        vals2 = kind2.value_set

        if vals1 != vals2:
            return False

        w1 = kind1.weights
        w2 = kind2.weights

        for v in vals1:
            weight1 = w1[v]
            weight2 = w2[v]

            # ATTN:check compatibility if as_nice_numeric(as_real(w1[v] - w2[v]).copy_abs()) >= tol:
            if is_numeric(weight1) and is_numeric(weight2):
                if not math.isclose(weight1, weight2, abs_tol=tol, rel_tol=tol):
                    return False
            elif weight1 != weight2:
                return False

        return True

    @classmethod
    def divergence(cls, kind1, kind2) -> Numeric:
        """Returns the Kullback-Leibler divergence of kind1 against kind2.

        Parameters:
          kind1, kind2 :: the kinds to compare

        Returns infinity if the kinds have different values, otherwise returns
            -sum_v w_1(v) log_2 w_2(v)/w_1(v)
        where the sum is over the common values of the two kinds.

        """
        if not isinstance(kind1, Kind) or not isinstance(kind2, Kind):
            raise KindError('Kind.divergence requires two arguments that are kinds.')

        if kind1.dim != kind2.dim or kind1.size != kind2.size:
            return RichReal(as_real('Infinity'))

        vals1 = kind1.value_set
        vals2 = kind2.value_set

        if vals1 != vals2:
            return RichReal(as_real('Infinity'))

        w1 = kind1.weights
        w2 = kind2.weights

        div = as_real('0')
        for v in vals1:
            div -= w1[v] * numeric_log2(w2[v] / w1[v])
        return RichReal(div)

    # The empty kind is a class datum; use a descriptor to please Python 3.10+
    empty = EmptyKindDescriptor()

    @staticmethod
    def table(kind):
        "DEPRECATED. "
        print(str(kind))

    # Calculations

    def mixture(self, cond_kind):
        """Kind Combinator: Creates a mixture kind with this kind as the mixer and `f_mapping` giving the targets.

        This is usually more easily handled by the >> operator, which takes the mixer on the
        left and the target on the right and is equivalent.

        It is recommended that `cond_kind` be a conditional Kind, though this function
        accepts a variety of formats as described below.

        Parameters
        ----------
          cond_kind - either a conditional Kind, a dictionary taking values of this
                      kind to other kinds, or a function doing the same. Every possible
                      value of this kind must be represented in the mapping. For scalar
                      kinds, the values in the dictionary or function can be scalars,
                      as they will be converted to the right form in this function.

        Returns a new mixture kind that combines the mixer and targets.

        """
        if isinstance(cond_kind, ConditionalKind):
            well_defined = cond_kind.well_defined_on(self.value_set)
            if well_defined is not True:
                raise KindError(well_defined)
            return self.bind(cond_kind)

        # This use case is discouraged for users but useful internally
        f = value_map(cond_kind, self)

        def join_values(vs):
            new_tree = f(vs)._canonical
            if len(new_tree) == 0:      # Empty result tree  (ATTN:CHECK)
                new_tree = [KindBranch.make(vs=(), p=1)]
            return Kind([KindBranch.make(vs=tuple(list(vs) + list(branch.vs)), p=branch.p) for branch in new_tree])

        return self.bind(join_values)

    def independent_mixture(self, kind_spec):
        """Kind Combinator: An independent mixture of this kind with another kind.

        This is usually more easily handled by the * operator, which is equivalent.

        Parameter `kind_spec` should be typically be a valid kind,
        but this will accept anything that produces a valid kind via
        the `kind()` function.

        Returns a new kind representing this mixture.

        """
        r_kind = kind(kind_spec)

        if len(r_kind) == 0:
            return self
        if len(self) == 0:
            return r_kind

        def combine_product(branchA, branchB):
            return KindBranch.make(vs=list(branchA.vs) + list(branchB.vs), p=branchA.p * branchB.p)

        return Kind([combine_product(brA, brB) for brA, brB in product(self._canonical, r_kind._canonical)])

    def transform(self, statistic):
        """Kind Combinator: Transforms this kind by a statistic, returning the transformed kind.

        Here, `statistic` is typically a Statistic object, though it
        can be a more general mapping or dictionary. It must have
        compatible dimension with this kind and be defined for all
        values of this kind.

        This is often more easily handled by the ^ operator, or by
        direct composition by the statistic, which are equivalent.
        The ^ notation is intended to evoke an arrow signifying the
        flow of data from the kind through the transform.

        """
        if isinstance(statistic, Statistic):
            lo, hi = statistic.codim
            if self.dim == 0 and lo == 0:
                # On Kind.empty, MonoidalStatistics return constant of their unit
                return constant(statistic())
            if lo <= self.dim <= hi:
                f = statistic
            else:  # Dimensions don't match, try it anyway?  (ATTN)
                try:
                    statistic(self._canonical[0].vs)
                    f = statistic
                except Exception:
                    raise KindError(f'Statistic {statistic.name} is incompatible with this kind: '
                                    f'acceptable dimension [{lo},{hi}] but kind dimension {self.dim}.')
        else:
            f = compose(as_vec_tuple, value_map(statistic))  # ATTN!
        return self.map(f)

    def conditioned_on(self, cond_kind):
        """Kind Combinator: computes the kind of the target conditioned on the mixer (this kind).

        This is usually more clearly handled with the // operator,
        which takes mixer // target.

        This is related to, but distinct from, a mixture in that it
        produces the kind of the target, marginalizing out the mixer
        (this kind). Conditioning is the operation of using
        hypothetical information about one kind and a contingent
        relationship between them to compute another kind.

        """
        if isinstance(cond_kind, ConditionalKind):
            well_defined = cond_kind.well_defined_on(self.value_set)
            if well_defined is not True:
                raise KindError(well_defined)
            return self.bind(cond_kind.target)

        # Function without input pass through
        try:
            cond_kind = value_map(cond_kind, self)
        except Exception:
            raise KindError('Conditioning on this kind requires a valid and '
                            'matching mapping of values to kinds of the same dimension')
        return self.bind(cond_kind)

    def expectation(self):
        """Computes the expectation of this kind. Scalar expectations are unwrapped. (Internal use.)

        The expectation should be computed using the E operator rather than this method.
        """
        ex = [as_numeric(0)] * self.dim
        for branch in self._canonical:
            for i, v in enumerate(branch.vs):
                ex[i] += branch.p * v
        return ex[0] if self.dim == 1 else as_vec_tuple(ex)

    def kernel(self, *v: ScalarQ | tuple[ScalarQ | QuantityType, ...], as_float=True ):
        """The kernel function associated with this Kind.

        The components of the value can be specified by a single tuple or multiple arguments.

        Parameters
          v : either a tuple or multiple arguments giving the components of tuple.
              Components can be any value that can be converted into a quantity,
              including symbols and numeric strings (e.g., '2/5').

          as_float [=True] : if True, convert result to a float; otherwise,
              returns a high-precision numeric quantity (Decimal)

        Returns the weight associated with value v, or 0 if not a possible value.

        """
        if len(v) == 1 and is_tuple(v[0]):
            value = v[0]
        else:
            value = v
        w = self.weights.get(as_quant_vec(value), 0)
        return float(w) if as_float else w

    def log_likelihood(self, data: Iterable[tuple[ScalarQ | ValueType, ...] | ScalarQ]) -> QuantityType:
        """The log-likelihood function for independent observations from this Kind.

        Accepts an iterable of n possible values of this Kind K, which are treated
        as an observation from (i.e., a possible value of) the Kind K ** n.

        Returns the log_likelihood of this observation from K ** n.

        This requires a Kind with numeric weights. (Not currently checked.)

        """
        log_likelihood = as_real('0')
        try:
            for datum in data:
                log_likelihood += numeric_ln(self.kernel(datum, as_float=False))  # type: ignore
        except Exception as e:
            raise KindError(f'Could not compute log likelihood for kind: {str(e)}')
        return log_likelihood

    @property
    def entropy(self) -> QuantityType:
        "The entropy of this Kind. Requires numeric weights."
        entropy = as_real(0)
        for branch in self._canonical:
            entropy += -branch.p * numeric_log2(branch.p)
        return entropy

    # Overloads

    def __eq__(self, other) -> bool:
        if not isinstance(other, Kind):
            return False
        return self._canonical == other._canonical

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._dimension > 0

    def __iter__(self):
        yield from ((b.p, b.vs) for b in self._canonical)

    def __mul__(self, other):
        "Mixes FRP with another independently"
        return self.independent_mixture(other)

    def __pow__(self, n, modulo=None):
        "Mixes FRP with itself n times independently"
        # Use monoidal power trick
        if n < 0:
            raise KindError('Kind powers with negative exponents not allowed')
        elif n == 0 or self.dim == 0:
            return Kind.empty
        elif n == 1:
            return self

        def combine_product(orig_branches):
            vs = []
            p = 1
            for b in orig_branches:
                vs.extend(b.vs)
                p *= b.p
            return KindBranch.make(vs=vs, p=p)

        return Kind([combine_product(obranches) for obranches in product(self._canonical, repeat=n)])

    def __rfloordiv__(self, other):
        """Kind Combinator: computes the kind of the target conditioned on the mixer.

        This as the form  ckind // mixer  where mixer is a Kind (this one) and
        ckind is a conditional Kind mapping values of the mixer to new kinds.

        This is equivalent to, but more efficient than,

              Proj[(mixer.dim + 1):](mixer >> ckind)

        That is, this produces the kind of the target marginalizing
        out the mixer's value. This is the operation of
        **Conditioning**: using hypothetical information about one
        kind and a contingent relationship between them to compute
        another kind.

        """

        "Conditioning on self; other is a conditional distribution."
        return self.conditioned_on(other)

    def __rshift__(self, cond_kind):
        """Returns a mixture kind with this kind as the mixer and `cond_kind` giving the targets.

        Here, `cond_kind` is typically a conditional Kind, though it
        can be a suitable function or dictionary. It must give a
        kind of common dimension for every value of this kind.

        The resulting kind has values concatenating the values of
        mixer and target. See also the // (.conditioned_on)
        operator, which is related. In particular, m // k is like k
        >> m without the values from k in the resulting kind.

        """
        return self.mixture(cond_kind)

    def __xor__(self, statistic):
        """Applies a statistic or other function to a Kind and returns a transformed kind.

        The ^ notation is intended to evoke an arrow signifying the flow of data
        from the kind through the transform.

        Here, `statistic` is typically a Statistic object, though it
        can be a more general mapping or dictionary. It must have
        compatible dimension with this kind and be defined for all
        values of this kind. When it is an actual Statistic,
        statistic(k) and k ^ statistic are equivalent.

        """
        return self.transform(statistic)

    def __rmatmul__(self, statistic):
        "Returns a transformed kind with the original kind as context for conditionals."
        if isinstance(statistic, Statistic):
            return TaggedKind(self, statistic)
        return NotImplemented

    # Need a protocol for ProjectionStatistic to satisfy to avoid circularity
    @overload
    def marginal(self, *__indices: int) -> 'Kind':
        ...

    @overload
    def marginal(self, __subspace: Iterable[int] | Projection | slice) -> 'Kind':
        ...

    def marginal(self, *index_spec) -> 'Kind':
        """Computes the marginalized kind, projecting on the given indices.

        This is usually handled in the playground with the Proj factory
        or by direct indexing of the kind.

        """
        dim = self.dim

        # Unify inputs
        if len(index_spec) == 0:
            return Kind.empty
        if isinstance(index_spec[0], Iterable):
            indices: tuple[int, ...] = tuple(index_spec[0])
        elif isinstance(index_spec[0], Projection):
            indices = tuple(index_spec[0].subspace)
        elif isinstance(index_spec[0], slice):
            start, stop, step = index_spec[0].indices(dim + 1)
            indices = tuple(range(max(start, 1), stop, step))
        else:
            indices = index_spec

        if len(indices) == 0:
            return Kind.empty

        # Check dimensions (allow negative indices python style)
        if any([index == 0 or index < -dim or index > dim for index in indices]):
            raise KindError( f'All marginalization indices in {indices} should be between 1..{dim} or -{dim}..-1')

        # Marginalize
        def marginalize(value):
            return tuple(map(lambda i: value[i - 1] if i > 0 else value[i], indices))
        return self.map(marginalize)

    def __getitem__(self, indices):
        "Marginalizing this kind; other is a projection index or list of indices (1-indexed)"
        return self.marginal(indices)

    def __or__(self, predicate):  # Self -> ValueMap[ValueType, bool] -> Kind[ValueType, ProbType]
        "Applies a conditional filter to a Kind."
        if isinstance(predicate, Condition):
            def keep(value):
                return predicate.bool_eval(value)
        elif isinstance(predicate, Statistic):
            def keep(value):
                result = predicate(value)
                return bool(as_scalar_strict(result))
        else:
            def keep(value):
                result = value_map(predicate)(value)   # ATTN: Why value_map here? Allows dict as condition
                return bool(as_scalar_strict(result))
        return Kind([branch for branch in self._canonical if keep(branch.vs)])

    def sample1(self):
        "Returns the value of one FRP with this kind."
        return VecTuple(self.sample(1)[0])

    def sample(self, n: int = 1):
        "Returns a list of values corresponding to `n` FRPs with this kind."
        if self._canonical:
            weights = []
            values = []
            for branch in self._canonical:
                if is_symbolic(branch.p):
                    raise EvaluationError(f'Cannot sample from a Kind/FRP with symbolic weight {branch.p}.'
                                          ' Try substituting values for the symbols first.')
                weights.append(float(branch.p))
                values.append(branch.vs)
        else:
            weights = [1]
            values = [vec_tuple()]
        # ATTN: Convert to iterator ??
        return lmap(VecTuple, random.choices(values, weights, k=n))

    def show_full(self) -> str:
        """Show a full ascii version of this kind as a tree in canonical form."""
        if len(self._canonical) == 0:
            return '<> -+'

        size = self.size
        juncture, extra = (size // 2, size % 2 == 0)

        p_labels = show_quantities(branch.p  for branch in self._canonical)
        v_labels = show_qtuples(branch.vs for branch in self._canonical)
        pwidth = max(map(len, p_labels), default=0) + 2

        lines = []
        if size == 1:
            plab = ' ' + p_labels[0] + ' '
            vlab = v_labels[0].replace(', -', ',-')  # ATTN:HACK fix elsewhere, e.g., '{0:-< }'.format(Decimal(-16.23))
            lines.append(f'<> ------{plab:-<{pwidth}}---- {vlab}')
        else:
            for i in range(size):
                plab = ' ' + p_labels[i] + ' '
                vlab = v_labels[i].replace(', -', ',-')   # ATTN:HACK fix elsewhere
                if i == 0:
                    lines.append(f'    ,----{plab:-<{pwidth}}---- {vlab}')
                    if size == 2:
                        lines.append('<> -|')
                        # lines.extend(['    |', '<> -|', '    |'])
                elif i == size - 1:
                    lines.append(f'    `----{plab:-<{pwidth}}---- {vlab}')
                elif i == juncture:
                    if extra:
                        lines.append( '<> -|')
                        lines.append(f'    |----{plab:-<{pwidth}}---- {vlab}')
                    else:
                        lines.append(f'<> -+----{plab:-<{pwidth}}---- {vlab}')
                else:
                    lines.append(f'    |----{plab:-<{pwidth}}---- {vlab}')
        return '\n'.join(lines)

    def __str__(self) -> str:
        return self.show_full()

    def __frplib_repr__(self):
        if environment.ascii_only:
            return str(self)
        return Panel(str(self), expand=False, box=box.SQUARE)

    def __repr__(self) -> str:
        if is_interactive():   # ATTN: Do we want this anymore??
            return self.show_full()  # So it looks nice at the repl
        return super().__repr__()

    def repr_internal(self) -> str:
        return f'Kind({repr(self._canonical)})'

    def serialize(self) -> str:
        "Returns the s-expression string representation of the Kind for serialization."
        return f'(<> {" ".join(str(b.p) + " " + str(b.vs) for b in self._canonical)})'

# Tagged kinds for context in conditionals
#
# phi@k acts exactly like phi(k) except in a conditional, where
#    phi@k | (s(k) == v)
# is like
#    (k * phi(k) | (s(Proj[:(d+1)](__)) == v))[(d+1):]
# but simpler
#

class TaggedKind(Kind):
    def __init__(self, createFrom, stat: Statistic):
        original = Kind(createFrom)
        super().__init__(original.transform(stat))
        self._original = original
        self._stat = stat

        lo, hi = stat.codim
        if self.dim < lo or self.dim > hi:
            raise MismatchedDomain(f'Statistic {stat.name} is incompatible with this Kind, '
                                   f'which has dimension {self.dim} out of expected range '
                                   f'[{lo}, {"infinity" if hi == math.inf else hi}].')

    def __or__(self, condition):
        return self._original.__or__(condition).transform(self._stat)

    def transform(self, statistic):
        # maybe some checks here
        new_stat = compose2(statistic, self._stat)
        return TaggedKind(self._original, new_stat)

    def _untagged(self):
        return (self._stat, self._original)


#
# Generalized Kind Constructor and Predicate
#
# See also the generic utilities size, dim, values, frp, unfold, clone, et cetera.

def kind(any) -> Kind:
    "A generic constructor for kinds, from strings, other kinds, FRPs, and more."
    if isinstance(any, Kind):
        return any
    # ATTN: Add case for conditional FRP to produce a conditional Kind
    #       Types(union) might be an issue downstream but probably not
    #       Maybe add a Kind property to ConditionalFRP to handle this?
    if hasattr(any, 'kind'):
        return any.kind

    if not any:
        return Kind.empty
    if isinstance(any, str) and (any in {'void', 'empty'} or re.match(r'\s*\(\s*<\s*>\s*\)\s*', any)):
        return Kind.empty

    if isinstance(any, SupportsKindOf):
        return any.kind_of()

    try:
        return Kind(any)
    except Exception as e:
        raise KindError(f'I could not create a Kind from {any}: {str(e)}')

def is_kind(x) -> TypeGuard[Kind]:
    return isinstance(x, Kind)


#
# Kind Utilities
#

@dataclass(frozen=True)
class UnfoldedKind:
    unfolded: list  # KindTree
    upicture: str

    def __str__(self) -> str:
        return self.upicture

    def __repr__(self) -> str:
        return repr(self.unfolded)

    def __frplib_repr__(self):
        if environment.ascii_only:
            return str(self)
        return Panel(str(self), expand=False, box=box.SQUARE)

def unfold(k: Kind) -> UnfoldedKind:  # ATTN: Return an object that prints this string, later
    if any(branch.is_symbolic() for branch in k._canonical):
        raise KindError('unfold on symbolic Kinds is not yet supported.')

    dim = k.dim
    unfolded = unfold_tree(k._canonical)
    if unfolded is None:
        return UnfoldedKind(k._canonical, k.show_full())
    # ATTN: Remove other components from this, no longer needed

    wd = [(0, 3)]  # Widths of the root node weight (empty) and value (<>)
    labelled = unfolded_labels(unfolded[1:], str(unfolded[0]), 1, wd)
    sep = [2 * (dim - level) for level in range(dim + 1)]  # seps should be even
    scan, _ = unfold_scan(labelled, wd, sep)

    return UnfoldedKind(unfolded, unfolded_str(scan, wd))

def clean(k: Kind, tolerance: ScalarQ = '1e-16') -> Kind:
    """Returns a new kind that eliminates from `k` any branches with numerically negligible weights.

    Weights < `tolerance` are assumed to be effectively zero and eliminated
    in the returned kind.

    Parameter `tolerance` can be any scalar quantity, including a string representing
    a decimal number or rational (no space around /).

    """
    # ATTN: new_normalize_branches above with _canonical=True can make this more efficient
    tol = as_real(tolerance)
    k = k ^ (lambda x: as_quant_vec(x, convert=as_nice_quantity))
    canonical = []
    for b in k._branches:
        if is_symbolic(b.p):
            pv = b.p.pure_value()
            if pv is None or pv >= tol:
                canonical.append(b)
        elif b.p >= tol:
            canonical.append(b)
    return Kind(canonical)

def bayes(observed_y, x, y_given_x):
    """Applies Bayes's Rule to find x | y == observed_y, a Kind or FRP.

    Takes an observed value of y, the kind/FRP x, and the conditional Kind/FRP
    y_given_x, reversing the conditionals.

    + `observed_y` is a *possible* value of a quantity y
    + `x` -- a Kind or FRP for a quantity x
    + `y_given_x` -- a conditional Kind or FRP (if x is an FRP) of y
          given the value of x.

    Returns a Kind if `x` is a Kind or FRP, if x is an FRP.

    """
    i = dim(x) + 1
    return (x >> y_given_x | (Proj[i:] == observed_y)) ^ Proj[1:i]

def fast_mixture_pow(mstat: MonoidalStatistic, k: Kind, n: int) -> Kind:
    """Efficiently computes the kind mstat(k ** n) for monoidal statistic `mstat`.

    Parameters
    ----------
    `mstat` :: An arbitrary monoidal statistic. If this is not monoidal, the computed
        kind may not be valid.
    `k` :: An arbitrary kind
    `n` :: A natural number

    Returns the kind mstat(k ** n) without computing k ** n directly.

    """
    if n < 0:
        raise KindError(f'fast_mixture_pow requires a non-negative power, given {n}.')
    if n == 0:
        return constant(mstat())
    if n == 1:
        return mstat(k)

    kn2 = fast_mixture_pow(mstat, k, (n // 2))

    if n % 2 == 0:
        return mstat(kn2 * kn2)
    return mstat(k * mstat(kn2 * kn2))


#
# Sequence argument interface for Kind factories
#

class Flatten(Enum):
    NOTHING = auto()
    NON_TUPLES = auto()
    NON_VECTORS = auto()
    EVERYTHING = auto()

def _is_sequence(x):
    return isinstance(x, Iterable) and not isinstance(x, str)

flatteners: dict[Flatten, Callable] = {
    Flatten.NON_TUPLES: lambda x: x if _is_sequence(x) and not isinstance(x, tuple) else [x],
    Flatten.NON_VECTORS: lambda x: x if _is_sequence(x) and not isinstance(x, VecTuple) else [x],
    Flatten.EVERYTHING: lambda x: x if _is_sequence(x) else [x],
}

ELLIPSIS_MAX_LENGTH: int = 10 ** 6

def sequence_of_values(
        *xs: Numeric | Symbolic | Iterable[Numeric | Symbolic] | Literal[Ellipsis],   # type: ignore
        flatten: Flatten = Flatten.NON_VECTORS,
        transform=identity,
        pre_transform=identity,
        parent=''
) -> list[Numeric | Symbolic]:
    # interface that reads values in various forms
    # individual values  1, 2, 3, 4
    # elided sequences   1, 2, ..., 10
    # iterables          [1, 2, 3, 4]
    # mixed sequences    1, 2, [1, 2, 3], 4, range(100,110), (17, 18)   with flatten=True only
    if flatten != Flatten.NOTHING:
        proto_values = list(chain.from_iterable(map(flatteners[flatten], map(pre_transform, xs))))
    elif len(xs) == 1 and isinstance(xs[0], Iterable):
        proto_values = list(pre_transform(xs[0]))
    else:
        proto_values = list(map(pre_transform, xs))

    values = []  # type: ignore
    n = len(proto_values)
    for i in range(n):
        value = proto_values[i]
        if value == Ellipsis:
            if i <= 1 or i == n - 1:
                raise KindError(f'Argument ... to {parent or "a factory"} must be appear in the pattern a, b, ..., c.')

            a, b, c = tuple(as_quantity(proto_values[j]) for j in [i - 2, i - 1, i + 1])

            if not is_numeric(a) or not is_numeric(b) or not is_numeric(c):
                raise ConstructionError('An ellipsis ... cannot be used between symbolic quantities')

            if c == a:  # singleton sequence, drop a and b
                values.pop()
                values.pop()
            elif c == b:  # pair, drop b
                values.pop()
            elif (a - b) * (b - c) <= 0:
                raise KindError(f'Argument ... to {parent or "a factory"} must be appear in the pattern a, b, ..., c '
                                f'with a < b < c or a > b > c.')
            elif numeric_abs(c - b) > numeric_abs(b - a) * ELLIPSIS_MAX_LENGTH:
                raise KindError(f'Argument ... to {parent or "a factory"} will lead to a very large sequence;'
                                f"I'm guessing this is a mistake.")
            else:
                values.extend([transform(b + k * (b - a))
                               for k in range(1, int(numeric_floor(as_real(c - b) / (b - a))))])
        else:
            values.append(transform(value))

    return values


#
# Kind Factories
#

void: Kind = Kind.empty

def constant(*xs: Numeric | Symbolic | Iterable[Numeric | Symbolic] | Literal[Ellipsis]) -> Kind:  # type: ignore
    """Kind Factory: returns the kind of a constant FRP with the specified value.

    Accepts any collection of symbolic or numeric values or
    iterables thereof and flattens this into a quantitative tuple
    which will be the single value `v` of the returned kind.

    Returns the kind <> --- <v>.

    """
    if len(xs) == 0:
        return Kind.empty
    value = as_quant_vec(sequence_of_values(*xs, flatten=Flatten.EVERYTHING))
    return Kind.unit(value)

def either(a, b, weight_ratio=1) -> Kind:
    """A choice between two possibilities a and b with ratio of weights (a to b) of `weight_ratio`.

    Values can be numbers, symbols, or strings. In the latter case they are converted
    to numeric or symbolic values as appropriate. Rational values in strings (e.g., '1/7')
    are allowed but must have no space around the '/'.

    """
    ratio = as_numeric(weight_ratio)
    p_a = ratio / (1 + ratio)
    return Kind([KindBranch.make(vs=as_quant_vec(a), p=p_a),
                 KindBranch.make(vs=as_quant_vec(b), p=1 - p_a)])

def uniform(*xs: Numeric | Symbolic | Iterable[Numeric | Symbolic] | Literal[Ellipsis]) -> Kind:   # type: ignore
    """Returns a Kind with equal weights on the given values.

    Values can be specified in a variety of ways:
      + As explicit arguments, e.g.,  uniform(1, 2, 3, 4)
      + As an implied sequence, e.g., uniform(1, 2, ..., 10)
        Here, two *numeric* values must be supplied before the ellipsis and one after;
        the former determine the start and increment; the latter the end point.
        Multiple implied sequences with different increments are allowed,
        e.g., uniform(1, 2, ..., 10, 12, ... 20)
        Note that the pattern a, b, ..., a will be taken as the singleton list a
        with b ignored, and the pattern a, b, ..., b produces [a, b].
      + As an iterable, e.g., uniform([1, 10, 20]) or uniform(irange(1,52))
      + With a combination of methods, e.g.,
           uniform(1, 2, [4, 3, 5], 10, 12, ..., 16)
        in which case all the values except explicit *tuples* will be
        flattened into a sequence of values. (Though note: all values
        should have the same dimension.)

    Values can be numbers, tuples, symbols, or strings. In the latter case they
    are converted to numbers or symbols as appropriate.

    Examples:
    + uniform(1, 2, 3)
    + uniform((0, 0), (0, 1), (1, 0), (1, 1)) 
    + uniform(1, 2, ..., 16)
    + uniform([10, 20, 30])
    + uniform( (x, y) for x in irange(1, 3) for y in irange(1, 3) )

    """
    values = sequence_of_values(*xs, flatten=Flatten.NON_TUPLES, transform=as_quant_vec)
    if len(values) == 0:
        return Kind.empty
    return Kind([KindBranch.make(vs=x, p=1) for x in values])

def symmetric(*xs, around=None, weight_by=lambda dist: 1 / dist if dist > 0 else 1) -> Kind:
    """Returns a Kind with the given values and weights a symmetric function of the values.

    Specifically, the weights are determined by the distance of each value
    from a specified value `around`:

           weight(x) = weight_by(distance(x, around))

    If `around` is specified it is used; otherwise, the mean of the values is used.
    The `weight_by` defaults to 1/distance, but can specified; it should be a function
    of one numeric parameter.

    Values can be specified in a variety of ways:
      + As explicit arguments, e.g.,  symmetric(1, 2, 3, 4)
      + As an implied sequence, e.g., symmetric(1, 2, ..., 10)
        Here, two *numeric* values must be supplied before the ellipsis and one after;
        the former determine the start and increment; the latter the end point.
        Multiple implied sequences with different increments are allowed,
        e.g., symmetric(1, 2, ..., 10, 12, ... 20)
        Note that the pattern a, b, ..., a will be taken as the singleton list a
        with b ignored, and the pattern a, b, ..., b produces [a, b].
      + As an iterable, e.g., symmetric([1, 10, 20]) or symmetric(irange(1,52))
      + With a combination of methods, e.g.,
           symmetric(1, 2, [4, 3, 5], 10, 12, ..., 16)
        in which case all the values except explicit *tuples* will be
        flattened into a sequence of values. (Though note: all values
        should have the same dimension.)

    Values can be numbers, tuples, or strings. In the latter case they
    are converted to numbers. If values are tuples, then either `around`
    should also be a tuple, or if that is not supplied, the tuples should
    first be passed to the qvec() function to make the distance computable.

    """
    if isinstance(around, tuple):  # We expect tuple values as well
        pre = as_numeric_vec
        post = identity
    else:
        pre = identity
        post = as_numeric_vec
    values = sequence_of_values(*xs, flatten=Flatten.NON_TUPLES, transform=pre)
    n = len(values)
    if n == 0:
        return Kind.empty
    if around is None:
        around = sum(values) / n  # type: ignore
    return Kind([KindBranch.make(vs=post(x), p=as_numeric(weight_by(abs(x - around)))) for x in values])

def linear(
        *xs: Numeric | Symbolic | Iterable[Numeric | Symbolic] | Literal[Ellipsis],  # type: ignore
        first=1,
        increment=1
) -> Kind:
    """Returns a Kind with the specified values and weights varying linearly

    Parameters
    ----------
    *xs: The values, see below.
    first: The weight associated with the first value. (Default: 1)
    increment: The increase in weight associated with each
        subsequent value. (Default: 1)

    Values can be specified in a variety of ways:
      + As explicit arguments, e.g.,  linear(1, 2, 3, 4)
      + As an implied sequence, e.g., linear(1, 2, ..., 10)
        Here, two *numeric* values must be supplied before the ellipsis and one after;
        the former determine the start and increment; the latter the end point.
        Multiple implied sequences with different increments are allowed,
        e.g., linear(1, 2, ..., 10, 12, ... 20)
        Note that the pattern a, b, ..., a will be taken as the singleton list a
        with b ignored, and the pattern a, b, ..., b produces [a, b].
      + As an iterable, e.g., linear([1, 10, 20]) or linear(irange(1,52))
      + With a combination of methods, e.g.,
           linear(1, 2, [4, 3, 5], 10, 12, ..., 16)
        in which case all the values except explicit *tuples* will be
        flattened into a sequence of values. (Though note: all values
        should have the same dimension.)

    Values can be numbers, tuples, symbols, or strings. In the latter case they
    are converted to numbers or symbols as appropriate.
    """
    values = sequence_of_values(*xs, flatten=Flatten.NON_TUPLES, transform=as_quant_vec)
    weights = [as_quantity(first + k * increment) for k in range(len(values))]

    return Kind([KindBranch.make(vs=x, p=w) for x, w in zip(values, weights)])

def geometric(
        *xs: Numeric | Symbolic | Iterable[Numeric | Symbolic] | Literal[Ellipsis],  # type: ignore
        first=1,
        r=0.5
) -> Kind:
    """Returns a Kind with the specified values and weights varying geometrically

    Parameters
    ----------
    *xs: The values, see below.
    first: The weight associated with the first value. (Default: 1)
    r: The the ratio between a weight and the preceding weight. (Default: 0.5)

    Values can be specified in a variety of ways:
      + As explicit arguments, e.g.,  geometric(1, 2, 3, 4)
      + As an implied sequence, e.g., geometric(1, 2, ..., 10)
        Here, two *numeric* values must be supplied before the ellipsis and one after;
        the former determine the start and increment; the latter the end point.
        Multiple implied sequences with different increments are allowed,
        e.g., geometric(1, 2, ..., 10, 12, ... 20)
        Note that the pattern a, b, ..., a will be taken as the singleton list a
        with b ignored, and the pattern a, b, ..., b produces [a, b].
      + As an iterable, e.g., geometric([1, 10, 20]) or geometric(irange(1,52))
      + With a combination of methods, e.g.,
           geometric(1, 2, [4, 3, 5], 10, 12, ..., 16)
        in which case all the values except explicit *tuples* will be
        flattened into a sequence of values. (Though note: all values
        should have the same dimension.)

    Values can be numbers, tuples, symbols, or strings. In the latter case they
    are converted to numbers or symbols as appropriate.
    """
    values = sequence_of_values(*xs, flatten=Flatten.NON_TUPLES, transform=as_quant_vec)
    ratio = as_quantity(r)
    w = as_quantity(first)
    weights = []
    for _ in values:
        weights.append(w)
        w = w * ratio
    return Kind([KindBranch.make(vs=x, p=w) for x, w in zip(values, weights)])

def weighted_by(*xs, weight_by: Callable) -> Kind:
    """Returns a Kind with the specified values weighted by a function of those values.

    Parameters
    ----------
    *xs: The values, see below.
    weight_by: A function that takes a value and returns a corresponding weight.

    Values can be specified in a variety of ways:
      + As explicit arguments, e.g.,  weighted_by(1, 2, 3, 4)
      + As an implied sequence, e.g., weighted_by(1, 2, ..., 10)
        Here, two *numeric* values must be supplied before the ellipsis and one after;
        the former determine the start and increment; the latter the end point.
        Multiple implied sequences with different increments are allowed,
        e.g., weighted_by(1, 2, ..., 10, 12, ... 20)
        Note that the pattern a, b, ..., a will be taken as the singleton list a
        with b ignored.
      + As an iterable, e.g., weighted_by([1, 10, 20]) or weighted_by(irange(1,52))
      + With a combination of methods, e.g.,
           weighted_by(1, 2, [4, 3, 5], 10, 12, ..., 16)
        in which case all the values except explicit *tuples* will be
        flattened into a sequence of values. (Though note: all values
        should have the same dimension.)

    Values and weights can be numbers, tuples, symbols, or strings.
    In the latter case they are converted to numbers or symbols as
    appropriate. `weight_by` must return a valid weight for all
    specified values.

    """
    values = sequence_of_values(*xs, flatten=Flatten.NON_TUPLES)
    if len(values) == 0:
        return Kind.empty
    return Kind([KindBranch.make(vs=as_quant_vec(x), p=as_quantity(weight_by(x))) for x in values])

def weighted_as(*xs, weights: Iterable[ScalarQ | Symbolic] = []) -> Kind:
    """Returns a Kind with the specified values weighted by given weights.

    Parameters
    ----------
    *xs: The values, see below.
    weights: A list of weights, one per given value. This must
        be specified as a named argument (e.g., weights=...)
        to distinguish it from the values.

    Values can be specified in a variety of ways:
      + As explicit arguments, e.g.,  weighted_as(1, 2, 3, 4)
      + As an implied sequence, e.g., weighted_as(1, 2, ..., 10)
        Here, two *numeric* values must be supplied before the ellipsis and one after;
        the former determine the start and increment; the latter the end point.
        Multiple implied sequences with different increments are allowed,
        e.g., weighted_as(1, 2, ..., 10, 12, ... 20)
        Note that the pattern a, b, ..., a will be taken as the singleton list a
        with b ignored, and the pattern a, b, ..., b produces [a, b].
      + As an iterable, e.g., weighted_as([1, 10, 20]) or weighted_as(irange(1,52))
      + With a combination of methods, e.g.,
           weighted_as(1, 2, [4, 3, 5], 10, 12, ..., 16)
        in which case all the values except explicit *tuples* will be
        flattened into a sequence of values. (Though note: all values
        should have the same dimension.)

    The list of weights can be specified with these same patterns,
    e.g., weights=[1, 2, ..., 4] or weights=[1, 2, [3, 4, 5], 6, 7, ..., 10],
    contained in a list or tuple. Weights can be any quantity, including
    symbols and strings representing fractions or high-precision decimals,
    e.g., '1/3'.

    Values and weights can be numbers, tuples, symbols, or strings.
    In the latter case they are converted to numbers or symbols as
    appropriate.

    Examples:
    + weighted_as(0, 1, weights=[1 - p, p])
    + weighted_as(1, 2, ..., 10, weights=[10, 9, ..., 1])
    + weighted_as(1, 2, 3, weights=['1/3', '1/2', '1/6'])
    + weighted_as( ((x, y) for x in irange(1, 3) for y in irange(1, 3)),
                    weights=[x + y for x in irange(1, 3) for y in irange(1, 3)] )
      (Note the parentheses around the value expression are needed here.)

    """
    if len(xs) == 1 and isinstance(xs[0], dict):
        # value: weight given in a dictionary
        val_wgt_map = xs[0]
        return Kind([KindBranch.make(vs=as_quant_vec(v), p=as_quantity(w))
                     for v, w in val_wgt_map.items()])

    values = sequence_of_values(*xs, flatten=Flatten.NON_TUPLES)
    if len(values) == 0:
        return Kind.empty

    kweights: list[Union[Numeric, Symbolic]] = sequence_of_values(*weights, flatten=Flatten.NON_TUPLES)
    if len(kweights) < len(values):
        kweights = [*kweights, *([1] * (len(values) - len(kweights)))]

    return Kind([KindBranch.make(vs=as_quant_vec(x), p=as_quantity(w))
                 for x, w in zip(values, kweights)])

def weighted_pairs(xs: Iterable[tuple[ValueType | ScalarQ, ScalarQ]]) -> Kind:
    """Returns a Kind specified by a sequence of (value, weight) pairs.

    Parameters
    ----------
    xs: An iterable of pairs of the form (value, weight).

    Values will be converted to quantitative vectors and weights
    to quantities. both can contain numbers, symbols, or strings.
    Repeated values will have their weights combined.

    Examples: 
    + weighted_pairs([(1, '1/2'), (2, '1/3'), (3, '1/6')])
    + weighted_pairs(((x, y), x + y) for x in irange(1, 3) for y in irange(1, 3))

    """
    return Kind([KindBranch.make(vs=as_quant_vec(v), p=as_quantity(w))
                 for v, w in xs])

def arbitrary(*xs, names: list[str] = []):
    "Returns a Kind with the given values and arbitrary symbolic weights."
    values = sequence_of_values(*xs, flatten=Flatten.NON_TUPLES, transform=as_numeric_vec)
    if len(values) == 0:
        return Kind.empty
    syms = lmap(symbol, names)
    for i in range(len(values) - len(syms)):
        syms.append(gen_symbol())
    return Kind([KindBranch.make(vs=x, p=sym) for x, sym in zip(values, syms)])

def integers(start, stop=None, step: int = 1, weight_fn=lambda _: 1):
    """Kind of an FRP whose values consist of integers from `start` to `stop` by `step`.

    If `stop` is None, then the values go from 0 to `tart`. Otherwise, the values
    go from `start` up to but not including `stop`.

    The `weight_fn` argument (default the constant 1) should be a function; it is
    applied to each integer to determine the weights.

    """
    if stop is None:
        stop = start
        start = 0
    if (stop - start) * step <= 0:
        return Kind.empty
    return Kind([KindBranch.make(vs=as_numeric_vec(x), p=weight_fn(x)) for x in range(start, stop, step)])

def evenly_spaced(start, stop=None, num: int = 2, weight_by=lambda _: 1):
    """Kind of an FRP whose values consist of evenly spaced numbers from `start` to `stop`.

    If `stop` is None, then the values go from 0 to `tart`. Otherwise, the values
    go from `start` up to but not including `stop`.

    The `weight_fn` argument (default the constant 1) should be a function; it is
    applied to each integer to determine the weights.

    """
    if stop is None:
        stop = start
        start = 0
    if math.isclose(start, stop) or num < 1:
        return Kind.empty
    if num == 1:
        return Kind.unit(start)
    step = abs(start - stop) / (num - 1)
    return Kind([KindBranch.make(vs=(x,), p=weight_by(x))
                 for i in range(num) if (x := start + i * step) is not None])

def without_replacement(n: int, xs: Iterable) -> Kind:
    """Kind of an FRP that samples n items from a set without replacement.

    The values of this kind do not distinguish between different orders
    of the sample. To get the kind of samples with order do

        permutations_of // without_replacement(n, xs)

    See `ordered_samples` for the factory that does this.

    """
    return Kind([KindBranch.make(vs=comb, p=1) for comb in combinations(xs, n)])

def subsets(xs: Collection, outside_element) -> Kind:
    """Kind of an FRP whose values are subsets of a given collection.

    Because the dimension needs to be consistent, outside_element,
    a value not in the collection, should be supplied to pad
    out the values.  This value should be comparable to the
    elements in the collection.

    The padding elements are placed at the beginning of the tuples
    so that the Kind sorts nicely. This may be changed in the future.

    """
    coll = list(xs)
    n = len(coll)
    power_set = chain.from_iterable(combinations(coll, n) for n in range(len(coll) + 1))
    annotated = starmap(lambda *v: as_vec_tuple((outside_element,) * (n - len(v)) + v), power_set)

    return Kind([KindBranch.make(vs=sub, p=1) for sub in annotated])

def ordered_samples(n: int, xs: Iterable) -> Kind:
    "Kind of an FRP whose values are all ordered samples of size `n` from the given collection."
    return permutations_of // without_replacement(n, xs)

def permutations_of(xs: Iterable, r=None) -> Kind:
    "Kind of an FRP whose values are permutations of a given collection."
    return Kind([KindBranch.make(vs=pi, p=1) for pi in permutations(xs, r)])

# ATTN: lower does not need to be lower just any bin boundary (but watch the floor below)
def bin(scalar_kind, lower, width):
    """Returns a Kind similar to that given but with values binned in specified intervals.

    The bins are intervals of width `width` starting at `lower`.  So, for instance,
    `lower` to `lower` + `width`, and so on.

    The given kind should be a scalar kind, or an error is raised.

    """
    if scalar_kind.dim > 1:
        raise KindError(f'Binning of non-scalar kinds (here of dimension {scalar_kind.dim} not yet supported')
    values: dict[tuple, Numeric] = {}
    for branch in scalar_kind._canonical:
        bin = ( lower + width * math.floor((branch.value - lower) / width), )
        if bin in values:
            values[bin] += branch.p
        else:
            values[bin] = branch.p
    return Kind([KindBranch.make(vs=v, p=p) for v, p in values.items()])


#
# Conditional Kinds
#

class ConditionalKind:
    """A unified representation of a conditional Kind.

    A conditional Kind is a mapping from a set of values of common
    dimension to Kinds of common dimension. This can be based
    on either a dictionary or on a function, though the dictionary
    is often more convenient in practice as we can determine the
    domain easily.

    This provides a number of facilities that are more powerful than
    working with a raw dictionary or function: nice output at the repl,
    automatic conversion of values, and automatic expectation computation
    (as a function from values to predictions). It is also more robust
    as this conversion performs checks and corrections.

    To create a conditional Kind, use the `conditional_kind` function,
    which see.

    """
    def __init__(
            self,
            mapping: Callable[[ValueType], Kind] | dict[ValueType, Kind] | dict[QuantityType, Kind] | Kind,
            *,
            codim: int | None = None,  # If set to 1, will pass a scalar not a tuple to fn (not dict)
            dim: int | None = None,    # If not supplied, this inferred in dict case
            domain: Iterable[ValueType] | Iterable[QuantityType] | Callable[[ValueType], bool] | None = None,
            target_dim: int | None = None   # ATTN: domain type in scalar callable case, blech
    ) -> None:
        has_domain_set = False
        if domain is not None:
            if callable(domain):
                self._domain: Callable[[ValueType], bool] = domain
            else:
                _domain_set: set = value_set_from(domain)  # Accessed in the following closure
                self._domain_set: set = _domain_set
                self._domain = lambda v: v in _domain_set
                has_domain_set = True
            self._trivial_domain = False
        else:
            # Infer domain set in the dict case later if possible
            self._domain = const(True)  # If unknown, accept everything
            self._trivial_domain = True

        if isinstance(mapping, Kind):
            target_dim = target_dim or mapping.dim
            mapping = const(mapping)

        if isinstance(mapping, dict):
            self._is_dict = True
            self._mapping: dict[ValueType, Kind] = {}
            self._targets: dict[ValueType, Kind] = {}  # NB: Trading space for time by keeping these
            for k, v in mapping.items():
                kin = as_quant_vec(k)
                vout = v.map(lambda u: VecTuple.concat(kin, u))  # Input pass through
                self._mapping[kin] = vout
                self._targets[kin] = v
            self._original_fn: Callable[[ValueType], Kind] | None = None

            # Attempt to infer codimension and domain if needed and possible.
            # We allow a) the dictionary to have extra keys, b) the Kinds to have
            # multiple dims if dim is supplied, c) the supplied domain to be a
            # subset of mapping's keys, d) the keys to have different dimensions
            # if codim is supplied.
            maybe_codims: set[int] = set()
            for k, v in self._mapping.items():
                maybe_codims.add(k.dim)

            if codim is None:
                if len(maybe_codims) == 1:
                    _codim: int | None = list(maybe_codims)[0]
                elif has_domain_set:
                    domain_dims = set(x.dim for x in self._domain_set)
                    if len(domain_dims) == 1:  # Known to have elements of only one dimension
                        _codim = list(domain_dims)[0]
                    else:
                        # This should not happen so raise an error
                        raise ConstructionError('Domain set for conditional Kind contains disparate dimensions')
                else:
                    _codim = None  # Cannot infer a single codim, accept any type of values
                    # raise ConstructionError('Cannot infer codimension of conditional Kind from given dict, '
                    #                         'please supply a codim argument or keys of common dimension')
            else:
                _codim = codim

            maybe_dims: set[int] = set()
            for k, v in self._mapping.items():
                if _codim is None or k.dim == _codim:
                    maybe_dims.add(v.dim)

            if dim is None and target_dim is None:
                if len(maybe_dims) == 1:
                    _dim: int | None = list(maybe_dims)[0]
                else:
                    _dim = None
                    # raise ConstructionError('Cannot infer dimension of conditional Kind from given dict, '
                    #                         'please supply a dim argument or Kinds of common dimension')
            elif dim is None:
                _dim = _codim + target_dim if _codim is not None else None  # type: ignore
            elif target_dim is None:
                if dim < min(maybe_dims):
                    raise ConstructionError('Specified dim for conditional Kind too small (must include input length), '
                                            'perhaps you meant to give the target_dim instead')
                _dim = dim
            elif _codim is not None and _codim != dim - target_dim:
                raise ConstructionError('Both dim and target_dim given but inconsistent, '
                                        'should have codim + target_dim = dim')
            else:  # both dim and target_dim supplied, either consistent with codim or with no codim
                if _codim is None:
                    if target_dim >= dim:
                        raise ConstructionError(f'target_dim {target_dim} should be smaller than dim {dim} '
                                                'for a Conditional Kind')
                    _codim = dim - target_dim  # Use this to infer codim, it's equivalent
                _dim = dim

            if domain is None:  # Infer domain set from keys
                if _codim is not None:
                    _domain_set = set(k for k in self._mapping.keys() if len(k) == _codim)
                else:
                    _domain_set = set(self._mapping.keys())
                self._domain_set = _domain_set
                self._domain = lambda v: v in _domain_set
                has_domain_set = True
                self._trivial_domain = False  # non-trivial domain specified implicitly
            elif has_domain_set:  # check that domains are consistent
                if _codim is not None:
                    mapping_domain = set(k for k in self._mapping.keys() if len(k) == _codim)
                else:
                    mapping_domain = set(self._mapping.keys())
                if not (self._domain_set <= mapping_domain):
                    raise ConstructionError('The supplied domain for a conditional Kind is not a subset of '
                                            'with the keys of the given dictionary.')

            self._codim: int | None = _codim
            self._dim: int | None = _dim
            self._has_domain_set = has_domain_set
            if target_dim is not None:
                self._target_dim: int | None = target_dim
            elif _codim is not None and _dim is not None:
                self._target_dim = _dim - _codim
            else:
                self._target_dim = None

            def fn(*args) -> Kind:
                n = len(args)
                if n == 1 and is_tuple(args[0]):
                    args = args[0]
                    n = len(args)
                value = as_quant_vec(args)  # ATTN: should this be as_vec_tuple??

                if self._codim is not None and n != self._codim:
                    raise MismatchedDomain(f'A value of invalid dimension {n} was passed to a'
                                           f' conditional Kind of codimension {self._codim}.')
                if (not self._trivial_domain and not self._domain(value)) or value not in self._mapping:
                    raise MismatchedDomain(f'Supplied value {value} not in domain of conditional Kind.')

                return self._mapping[value]

            def tfn(*args) -> Kind:
                n = len(args)
                if n == 1 and is_tuple(args[0]):
                    args = args[0]
                    n = len(args)
                value = as_quant_vec(args)  # ATTN: should this be as_vec_tuple??

                if self._codim is not None and n != self._codim:
                    raise MismatchedDomain(f'A value of invalid dimension {n} was passed to a'
                                           f' conditional Kind of codimension {self._codim}.')
                if (not self._trivial_domain and not self._domain(value)) or value not in self._targets:
                    raise MismatchedDomain(f'Supplied value {value} not in domain of conditional Kind.')

                return self._targets[value]

            self._fn: Callable[..., Kind] = fn
            self._target_fn: Callable[..., Kind] = tfn
        elif callable(mapping):         # Check to please mypy
            self._is_dict = False
            self._mapping = {}
            self._targets = {}  # NB: Trading space for time by keeping these
            self._original_fn = mapping

            if codim is None:
                domain_dims = set()
                if has_domain_set:
                    domain_dims = set(x.dim for x in self._domain_set)

                if has_domain_set and len(domain_dims) == 1:  # Known to have elements of only one dimension
                    _codim = list(domain_dims)[0]
                else:
                    _codim = None  # Cannot infer a single codim, accept any type of values
                    # raise ConstructionError('Cannot infer codimension of conditional Kind from given dict, '
                    #                         'please supply a codim argument or keys of common dimension')
            else:
                _codim = codim

            if _codim == 1:  # Account for scalar functions from user
                if domain is not None and not has_domain_set:
                    # domain is a function assumed to take a scalar, so we unwrap it
                    original_domain = self._domain
                    self._domain = lambda v: original_domain(as_scalar_weak(v))
                # function is assumed to take a scalar, so we unwrap it
                original_fn = mapping
                mapping = scalar_safe(original_fn)

            if dim is None and target_dim is None:
                _dim = None
                # raise ConstructionError('Cannot infer dimension of conditional Kind from given function, '
                #                         'please supply a dim or target_dim argument')
            elif dim is None:
                _dim = _codim + target_dim if _codim is not None else None  # type: ignore
            elif target_dim is None:
                if _codim is not None and dim <= _codim:
                    raise ConstructionError('Specified dim for conditional Kind too small (must include input length), '
                                            'perhaps you meant to give the target_dim instead')
                _dim = dim
            elif _codim is not None and _codim != dim - target_dim:
                raise ConstructionError('Both dim and target_dim given but inconsistent, '
                                        'should have codim + target_dim = dim')
            else:
                if _codim is None:
                    if target_dim >= dim:
                        raise ConstructionError(f'target_dim {target_dim} should be smaller than dim {dim} '
                                                'for a Conditional Kind')
                    _codim = dim - target_dim  # Use this to infer codim, it's equivalent
                _dim = dim

            self._codim = _codim
            self._dim = _dim
            self._has_domain_set = has_domain_set
            if target_dim is not None:
                self._target_dim = target_dim
            elif _codim is not None and _dim is not None:
                self._target_dim = _dim - _codim
            else:
                self._target_dim = None

            assert callable(mapping)  # For mypy

            def fn(*args) -> Kind:
                n = len(args)
                if n == 1 and is_tuple(args[0]):
                    args = args[0]
                    n = len(args)
                value = as_quant_vec(args)  # ATTN: should this be as_vec_tuple??

                if self._codim is not None and n != self._codim:
                    raise MismatchedDomain(f'A value of invalid dimension {n} was passed to a'
                                           f' conditional Kind of codimension {self._codim}.')
                if not self._trivial_domain and not self._domain(value):
                    raise MismatchedDomain(f'Supplied value {value} not in domain of conditional Kind.')

                if value in self._mapping:
                    return self._mapping[value]
                try:
                    result = mapping(value)
                except Exception as e:
                    raise MismatchedDomain(f'encountered a problem passing {value} to a conditional Kind: {str(e)}')

                extended = result.map(lambda u: VecTuple.concat(value, u))  # Input pass through
                self._mapping[value] = extended   # Cache, fn should be pure
                self._targets[value] = result     # Store unextended to ease some operations
                return extended

            def tfn(*args) -> Kind:
                n = len(args)
                if n == 1 and is_tuple(args[0]):
                    args = args[0]
                    n = len(args)
                value = as_quant_vec(args)  # ATTN: should this be as_vec_tuple??

                if self._codim is not None and n != self._codim:
                    raise MismatchedDomain(f'A value of invalid dimension {n} was passed to a'
                                           f' conditional Kind of codimension {self._codim}.')
                if not self._trivial_domain and not self._domain(value):
                    raise MismatchedDomain(f'Supplied value {value} not in domain of conditional Kind.')

                if value in self._targets:
                    return self._targets[value]
                try:
                    result = mapping(value)
                except Exception as e:
                    raise MismatchedDomain(f'encountered a problem passing {value} to a conditional Kind: {str(e)}')

                extended = result.map(lambda u: VecTuple.concat(value, u))  # Input pass through
                self._mapping[value] = extended   # Cache, fn should be pure
                self._targets[value] = result     # Store unextended to ease some operations
                return result

            self._fn = fn
            self._target_fn = tfn

    def __call__(self, *value) -> Kind:
        return self._fn(*value)

    def __getitem__(self, *value) -> Kind:
        "Returns this conditional Kind's target associated with the key."
        return self._target_fn(*value)

    def target(self, *value) -> Kind:
        return self._target_fn(*value)

    @property
    def dim(self):
        return self._dim

    @property
    def codim(self):
        return self._codim

    @property
    def type(self):
        codim = f'{self._codim}' if self._codim is not None else '*'

        if self._dim is not None:
            dim = f'{self._dim}'
        elif self._codim is None and self._dim is None and self._target_dim is not None:
            dim = f'* + {self._target_dim}'
        else:
            dim = '*'

        return f'{codim} -> {dim}'

    def is_in_domain(self, v):
        """Tests whether a value belongs to the specified domain of a Conditional Kind.

        If the domain was not specified, this will return True for every value.

        """
        return self._domain(as_vec_tuple(v))

    def kind_of(self) -> 'ConditionalKind':
        return self

    def clone(self) -> 'ConditionalKind':
        "Returns a clone of this conditional Kind, which being immutable is itself."
        return self

    def map(self, transform) -> dict | Callable:
        """Returns a dictionary or function like this conditional Kind applying `transform` to each target Kind.

        The Kinds in this dictionary do *not* include the input, nor does the transform see the input.
        For that, see the `transform` method.

        This is for specialized uses; users will almost always prefer to use `ConditionalKind.transform`.

        """
        if self._is_dict:
            return {k: transform(v) for k, v in self._targets.items()}

        fn = self._target_fn

        def trans_map(*x):
            return transform(fn(*x))
        return trans_map

    def expectation(self) -> Callable:
        """Returns a function from values to the expectation of the corresponding target Kind.

        The domain, dim, and codim of the returned function are each specified as attributes
        attribute ('domain', 'dim', and 'codim', respectively). These may be None if unavailable.

        """
        def fn(*x):
            k = self._target_fn(*x)
            return k.expectation()

        setattr(fn, 'codim', self._codim)
        if self._codim is not None and self._dim is not None:
            setattr(fn, 'dim', self._dim - self._codim)
        elif self._target_dim is not None:
            setattr(fn, 'dim', self._target_dim)
        else:
            setattr(fn, 'dim', None)
        setattr(fn, 'domain', self._domain if not self._trivial_domain else None)

        return fn

    def kernel(self, v, x, as_float=True):
        """The kernel function K(v | x) of this conditional Kind.

        Returns the weight on the v branch of the target associated
        with x or 0 if there is no v branch. By default this
        is converted to a float, but set as_float=False for a
        high-precision Decimal.

        Raises an error if x is not a valid input value.

        """
        k = self.target(as_vec_tuple(x))
        return k.kernel(v, as_float=as_float)

    def well_defined_on(self, values) -> Union[bool, str]:
        "If possible, check that every value is in the domain."
        val_set = value_set_from(values)
        non_trivial = not self._trivial_domain
        has_codim = self._codim is not None
        for v in val_set:
            if (has_codim and v.dim != self._codim) or (non_trivial and not self._domain(v)):
                return (f'A conditional Kind is not defined on all the values requested of it, '
                        f'including {v}')
        return True

    def __str__(self) -> str:
        pad = ': '
        tbl = '\n\n'.join([show_labeled(self.target(k), str(k) + pad)
                           for k in sorted(self._mapping.keys(), key=tuple) if self._domain(k)])
        dlabel = f' with domain={str(self._domain_set)}.' if self._has_domain_set else ''
        tlabel = f' of type {self.type}'

        if self._is_dict or (self._has_domain_set and self._domain_set == set(self._mapping.keys())):
            title = f'A conditional Kind{tlabel} with wiring:\n'
            return title + tbl
        elif tbl:
            mlabel = f'.\nIt\'s wiring includes:\n{tbl}\n  ...more kinds\n'
            return f'A conditional Kind{tlabel} as a function{dlabel or mlabel or "."}'
        return f'A conditional Kind{tlabel} as a function{dlabel or "."}'

    def __frplib_repr__(self):
        if environment.ascii_only:
            return str(self)
        return Panel(str(self), expand=False, box=box.SQUARE)

    def __repr__(self) -> str:
        if environment.is_interactive:
            return str(self)
        label = ''
        if self._codim is not None:
            label = label + f', codim={repr(self._codim)}'
        if self._dim is not None:
            label = label + f', dim={repr(self._dim)}'
        if self._target_dim is not None:
            label = label + f', target_dim={repr(self._target_dim)}'
        if self._has_domain_set:
            label = label + f', domain={repr(self._domain_set)}'
        else:
            label = label + f', domain={repr(self._domain)}'
        if self._is_dict or (self._has_domain_set and self._domain_set == set(self._mapping.keys())):
            return f'ConditionalKind({repr(self._targets)}{label})'
        else:
            return f'ConditionalKind({repr(self._target_fn)}{label})'

    # Kind operations lifted to Conditional Kinds

    def transform(self, statistic) -> ConditionalKind:
        if not isinstance(statistic, Statistic):
            raise KindError('A conditional Kind can be transformed only by a Statistic.'
                            ' Consider passing this tranform to `conditional_kind` first.')
        lo, hi = statistic.codim
        if self._dim is not None and (self._dim < lo or self._dim > hi):
            raise KindError(f'Statistic {statistic.name} is incompatible with this kind: '
                            f'acceptable dimension [{lo},{hi}] but kind dimension {self._dim}.')

        if self._trivial_domain:
            domain: set[ValueType] | Callable[[ValueType], bool] | None = None
        elif self._has_domain_set:
            domain = self._domain_set
        else:
            domain = self._domain

        s_dim = statistic.dim

        if self._is_dict:
            f_mapping = {k: statistic(v) for k, v in self._mapping.items()}
            return ConditionalKind(f_mapping, codim=self._codim, target_dim=s_dim, domain=domain)

        if self._dim is not None:
            def transformed(*value):
                return statistic(self._fn(*value))
        else:
            def transformed(*value):
                try:
                    return statistic(self._fn(*value))
                except Exception:
                    raise KindError(f'Statistic {statistic.name} appears incompatible with this conditional Kind.')
        return ConditionalKind(transformed, codim=self._codim, target_dim=s_dim, domain=domain)

    def __xor__(self, statistic):
        return self.transform(statistic)

    def transform_targets(self, statistic) -> ConditionalKind:
        if not isinstance(statistic, Statistic):
            raise KindError('A conditional Kind can be transformed only by a Statistic.'
                            ' Consider passing this tranform to `conditional_kind` first.')
        lo, hi = statistic.codim
        have_dim_codim = self._dim is not None and self._codim is not None
        if have_dim_codim or self._target_dim is not None:
            d = self._dim - self._codim if have_dim_codim else self._target_dim  # type: ignore
            if d < lo or d > hi:                                                 # type: ignore
                raise KindError(f'Statistic {statistic.name} is incompatible with this conditional Kind: '
                                f'acceptable dimension [{lo},{hi}] but target Kind dimension {d}.')

        if self._trivial_domain:
            domain: set[ValueType] | Callable[[ValueType], bool] | None = None
        elif self._has_domain_set:
            domain = self._domain_set
        else:
            domain = self._domain

        s_dim = statistic.dim

        if self._is_dict:
            f_mapping = {k: statistic(v) for k, v in self._targets.items()}
            return ConditionalKind(f_mapping, codim=self._codim, target_dim=s_dim, domain=domain)

        def transformed(*value):
            return statistic(self._target_fn(*value))
        return ConditionalKind(transformed, codim=self._codim, target_dim=s_dim, domain=domain)

    def __rshift__(self, ckind):
        if not isinstance(ckind, ConditionalKind):
            return NotImplemented

        if self._dim != ckind._codim:
            raise OperationError('Incompatible mixture of conditional Kinds, '
                                 f'{self.type} does not match {ckind.type}')

        if self._has_domain_set:
            domain: set[ValueType] | Callable[[ValueType], bool] | None = self._domain_set
        elif not self._trivial_domain:
            domain = self._domain
        else:
            domain = None

        # ATTN: Can optimize for the case where self._codim is not None
        # proj = drop_input(self._codim)

        # For dict or function with whole domain seen, use a dict; otherwise wrap the function
        if self._is_dict or (self._has_domain_set and self._domain_set == set(self._mapping.keys())):
            mapping = {given: (kind >> ckind).map(drop_input(len(given))) for given, kind in self._mapping.items()}
            return ConditionalKind(mapping, codim=self._codim, dim=ckind._dim, domain=domain)

        def mixed(*given):
            return (self(*given) >> ckind).map(drop_input(len(given)))
        return ConditionalKind(mixed, codim=self._codim, dim=ckind._dim, domain=domain)

    def __mul__(self, ckind):
        "A conditional Kind from the independent mixture of targets for conditional Kinds of equal codim."
        if not isinstance(ckind, ConditionalKind):
            return NotImplemented

        if self._codim is None or ckind._codim != self._codim:
            raise OperationError('For conditional Kinds, * requires both to have fixed codimensions')

        if self._dim is None or ckind._dim is None:
            mdim: int | None = None
        else:
            mdim = self._dim + ckind._dim - ckind._codim

        if self._codim is None or ckind._codim != self._codim:
            raise OperationError('For conditional Kinds, * requires both to have fixed codimensions')

        if self._has_domain_set and ckind._has_domain_set:
            domain = self._domain_set & ckind._domain_set
        else:
            # ATTN: domain function should also be checked and used where appropriate
            domain = None

        if self._is_dict and ckind._is_dict:
            s_domain = (self._has_domain_set and self._domain_set) or self._mapping.keys()
            c_domain = (ckind._has_domain_set and ckind._domain_set) or ckind._mapping.keys()
            intersecting = s_domain & c_domain
            mapping = {given: self._targets[given] * ckind._targets[given] for given in intersecting}

            return ConditionalKind(mapping, codim=self._codim, dim=mdim, domain=domain)

        def mixed(*given):
            return self._target_fn(*given) * ckind._target_fn(*given)

        return ConditionalKind(mixed, codim=self._codim, dim=mdim, domain=domain)

def conditional_kind(
        mapping: Callable[[ValueType], Kind] | dict[ValueType, Kind] | dict[QuantityType, Kind] | Kind | None = None,
        *,
        codim: int | None = None,
        dim: int | None = None,
        domain: Iterable[ValueType] | Callable[[ValueType], bool] | None = None,
        target_dim: int | None = None
) -> ConditionalKind | Callable[..., ConditionalKind]:
    """Converts a mapping from values to FRPs into a conditional FRP.

    The mapping can be a dictionary associating values (vector tuples)
    to FRPs or a function associating values to kindss. In the latter
    case, a `domain` set can be supplied for validation.

    The dictionaries can be specified with scalar keys as these are automatically
    wrapped in a tuple. If you want the function to accept a scalar argument
    rather than a tuple (even 1-dimensional), you should supply codim=1.

    The `codim`, `dim`, and `domain` arguments are used for compatibility
    checks, except for the codim=1 case mentioned earlier. `domain` is the
    set of possible values which can be supplied when mapping is a function
    (or used as a decorator).

    If mapping is missing, this function can acts as a decorator on the
    function definition following.

    Returns a ConditionalKind (if mapping given) or a decorator.

    """
    if mapping is not None:
        return ConditionalKind(mapping, codim=codim, dim=dim, domain=domain, target_dim=target_dim)

    def decorator(fn: Callable) -> ConditionalKind:
        return ConditionalKind(fn, codim=codim, dim=dim, domain=domain, target_dim=target_dim)
    return decorator

def is_conditional_kind(x) -> TypeGuard[Union[Kind, ConditionalKind]]:
    return isinstance(x, Kind) or isinstance(x, ConditionalKind)


#
# Provisional for incorporation and testing
#

def show_labeled(kind, label, width=None):
    width = width or len(label) + 1
    label = f'{label:{width}}'
    return re.sub(r'^.*$', lambda m: label + m[0] if re.match(r'\s*<>', m[0]) else (' ' * width) + m[0],
                  str(kind), flags=re.MULTILINE)


def tbl(mix, pad=': '):
    print( '\n\n'.join([show_labeled(mix[k], str(k) + pad) for k in mix]))


#
# Info tags
#

setattr(kind, '__info__', 'kind-factories::kind')
setattr(conditional_kind, '__info__', 'kind-factories')
setattr(constant, '__info__', 'kind-factories::constant')
setattr(uniform, '__info__', 'kind-factories::uniform')
setattr(either, '__info__', 'kind-factories::either')
setattr(weighted_as, '__info__', 'kind-factories::weighted_as')
setattr(weighted_by, '__info__', 'kind-factories')
setattr(weighted_pairs, '__info__', 'kind-factories')
setattr(symmetric, '__info__', 'kind-factories')
setattr(linear, '__info__', 'kind-factories')
setattr(geometric, '__info__', 'kind-factories')
setattr(arbitrary, '__info__', 'kind-factories')
setattr(integers, '__info__', 'kind-factories')
setattr(evenly_spaced, '__info__', 'kind-factories')
setattr(without_replacement, '__info__', 'kind-factories')
setattr(subsets, '__info__', 'kind-factories')
setattr(permutations_of, '__info__', 'kind-factories')
setattr(bin, '__info__', 'kind-combinators::bin')
setattr(unfold, '__info__', 'actions')
setattr(clean, '__info__', 'actions')
setattr(fast_mixture_pow, '__info__', 'kind-combinators::fast_mixture_pow')
setattr(bayes, '__info__', 'kind-combinators')
