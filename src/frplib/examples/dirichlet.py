# Dirichlet Solutions Example from Section 6

__all__ = ['solve_dirichlet', 'solve_dirichlet_sparse', 'K_NSEW', 'lava_room']

from frplib.exceptions import InputError
from frplib.frps       import frp
from frplib.kinds      import conditional_kind, uniform, weighted_as
from frplib.utils      import clone


@conditional_kind
def K_NSEW(tile):
    x, y = tile
    return uniform( (x - 1, y), (x, y - 1), (x, y + 1), (x + 1, y) )


def solve_dirichlet(cKind, *, fixed, fixed_values, alpha=0, beta=1, states=None):
    """Solves a Dirichlet problem determined by a conditional Kind and boundary constraints.

    Specifically, we want to solve for a function f on the domain of cKind
    that satisfies

       f(s) = fixed_values[i] when s in fixed[i] for some i, and
       f(s) = alpha + beta E(f(cKind(s))) otherwise.

    Parameters
      + cKind: ConditionalKind - determines Kind of transition from each state.
            Its domain is the set of possible states if explicitly available
            and the states parameter is not supplied.
      + fixed: list[set] - disjoint subsets of states on which f's value is known
      + fixed_values: list[float] - known values of f corresponding to fixed set
            in the same position. Must have the same length as fixed.
      + alpha: float [=0] - step cost parameter
      + beta: float [=1] - scaling parameter
      + states: None | Iterable - if supplied, the set of states that defines the domain
            of the function f.  If not supplied, must be obtainable explicitly
            from cKind.

    Returns a function of states (as tuples or multiple arguments)
    representing the solution f.

    """
    pass

def solve_dirichlet_sparse(cKind, *, fixed, fixed_values, alpha=0, beta=1, states=None):
    """Solves a Dirichlet problem determined by a conditional Kind and boundary constraints.

    Specifically, we want to solve for a function f on the domain of cKind
    that satisfies

       f(s) = fixed_values[i] when s in fixed[i] for some i, and
       f(s) = alpha + beta E(f(cKind(s))) otherwise.

    Parameters
      + cKind: ConditionalKind - determines Kind of transition from each state.
            Its domain is the set of possible states if explicitly available
            and the states parameter is not supplied.
      + fixed: list[set] - disjoint subsets of states on which f's value is known
      + fixed_values: list[float] - known values of f corresponding to fixed set
            in the same position. Must have the same length as fixed.
      + alpha: float [=0] - step cost parameter
      + beta: float [=1] - scaling parameter
      + states: None | Iterable - if supplied, the set of states that defines the domain
            of the function f.  If not supplied, must be obtainable explicitly
            from cKind.

    Returns a function of states (as tuples or multiple arguments)
    representing the solution f.

    """
    pass


# Example System in Text

lava_room = 'A room filled with lava and cool water arranged on a regular grid'
setattr(lava_room, 'states', [])
setattr(lava_room, 'fixed', [{}, {}])
