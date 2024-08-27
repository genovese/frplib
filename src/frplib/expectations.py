from __future__ import annotations

from collections.abc   import Iterable
from functools         import wraps

from frplib.exceptions import ComplexExpectationWarning
from frplib.frps       import FRP, ConditionalFRP
from frplib.kinds      import Kind, ConditionalKind
from frplib.output     import in_panel
from frplib.protocols  import SupportsExpectation, SupportsApproxExpectation, SupportsForcedExpectation
from frplib.quantity   import show_qtuple
from frplib.statistics import Statistic, statistic, __, Proj
from frplib.utils      import codim, dim
from frplib.vec_tuples import VecTuple, as_vec_tuple


class Expectation(VecTuple):
    def __init__(self, contents: Iterable):
        self.label = ''

    def __str__(self) -> str:
        return show_qtuple(self)

    def __frplib_repr__(self):
        return in_panel(str(self), title=self.label or None)

    # ATTN: needed?
    @property
    def raw(self):
        "Expectation as a raw scalar or vector tuple."
        if len(self) == 1:
            return self[0]
        return VecTuple(self)

def E(x, force_kind=False, allow_approx=True, tolerance=0.01):
    """Computes and returns the expectation of a given object.

    If `x` is an FRP or Kind, its expectation is computed directly,
    unless doing so seems computationally inadvisable. In this case,
    the expectation is forced if `forced_kind` is True and otherwise
    is approximated, with specified `tolerance`, if `allow_approx`
    is True.

    In this case, returns a quantity wrapping the expectation that
    allows convenient display at the repl; the actual value is in
    the .this property of the returned object.

    If `x` is a ConditionalKind or ConditionalFRP, then returns
    a *function* from domain values in the conditional to
    expectations.

    """
    if isinstance(x, (ConditionalKind, ConditionalFRP)):
        f = x.expectation()
        codim = getattr(f, 'codim')
        dim = getattr(f, 'dim')
        codim_str = f'{codim}' if codim is not None else '*'
        dim_str = f'{dim}' if dim is not None else '*'
        f_type = f'{codim_str} -> {dim_str}'

        @wraps(f)
        def c_expectation(*xs):
            e = f(*xs)
            if e is None:  # ATTN: None case was deprecated, can remove
                return None
            return Expectation(as_vec_tuple(e))
        setattr(c_expectation, '__frplib_repr__',
                lambda: f'A conditional expectation as a function of type {f_type}.')
        return c_expectation

    if isinstance(x, SupportsExpectation):
        label = ''
        try:
            expect = x.expectation()
        except ComplexExpectationWarning as e:
            if force_kind and isinstance(x, SupportsForcedExpectation):
                expect = x.forced_expectation()
            elif isinstance(x, SupportsApproxExpectation):
                expect = x.approximate_expectation(tolerance)
                label = (f'Computing approximation (tolerance {tolerance}) '
                         f'as exact calculation may be costly')  # ': {str(e)}\n'
            else:
                raise e
        expect = Expectation(as_vec_tuple(expect))
        if label:
            expect.label = label
        return expect
    return None

def Var(x, force_kind=False, allow_approx=True, tolerance=0.01):
    """Computes and returns the variance of a given object.

    Note: Currently only supports scalar expectations.

    If `x` is an FRP or Kind, its variance is computed directly,
    unless doing so seems computationally inadvisable. In this case,
    the variance is forced if `forced_kind` is True and otherwise
    is approximated, with specified `tolerance`, if `allow_approx`
    is True.

    In this case, returns a quantity wrapping the expectation that
    allows convenient display at the repl; the actual value is in
    the .this property of the returned object.

    If `x` is a ConditionalKind or ConditionalFRP, then returns
    a *function* from domain values in the conditional to
    variances.

    """
    if isinstance(x, (ConditionalKind, ConditionalFRP)):
        c = codim(x)
        d = dim(x)
        if c is None or d is None or d - c != 1:
            raise ComplexExpectationWarning('Var currently only supports scalar targets in conditional Kinds/FRPs.')

        e = E(x)

        @statistic(codim=d, dim=1)
        def ex(v):
            return e(v[:-1]).raw

        y = x.transform((Proj[-1] - ex) ** 2)
        f = E(y)
        setattr(f, '__frplib_repr__',
                lambda: f'A conditional variance as a function of type {str(c) if c else "*"} -> 1.')
        return f

    if isinstance(x, SupportsExpectation):
        if dim(x) != 1:
            raise ComplexExpectationWarning('Var currently only supports scalar Kinds/FRPs.')

        e = E(x)
        return E(x ^ (__ - e)**2 )

    return None


def D_(X: FRP | Kind):
    """The distribution operator for an FRP or kind.

    When passed an FRP or kind, this returns a function
    that maps any compatible statistic to the expectation
    of the transformed FRP or kind.

    """
    def probe(psi: Statistic):
        # ATTN: Check compatibility here
        return E(psi(X))
    return probe


#
# Info tags
#

setattr(E, '__info__', 'actions')
setattr(D_, '__info__', 'actions')
