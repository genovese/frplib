from __future__ import annotations

from frplib.exceptions import ComplexExpectationWarning
from frplib.frps       import FRP, ConditionalFRP
from frplib.kinds      import Kind, ConditionalKind
from frplib.numeric    import show_tuple
from frplib.output     import TitledRichFacade
from frplib.protocols  import SupportsExpectation, SupportsApproxExpectation, SupportsForcedExpectation
from frplib.statistics import Statistic
from frplib.vec_tuples import as_vec_tuple


def E(x, force_kind=False, allow_approx=True, tolerance=0.01):
    """Computes and returns the expectation of a given object.

    If `x` is an FRP or kind, its expectation is computed directly,
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
        return x.expectation()

    if isinstance(x, SupportsExpectation):
        title = ''
        try:
            expect = x.expectation()
        except ComplexExpectationWarning as e:
            if force_kind and isinstance(x, SupportsForcedExpectation):
                expect = x.forced_expectation()
            elif isinstance(x, SupportsApproxExpectation):
                expect = x.approximate_expectation(tolerance)
                title = (f'Computing approximation (tolerance {tolerance}) '
                         f'as exact calculation may be costly: {str(e)}\n')
            else:
                raise e

        expect = as_vec_tuple(expect)
        return TitledRichFacade(expect, show_tuple(expect), title)
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
