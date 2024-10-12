# Dirichlet Solutions Example from Section 6

__all__ = ['solve_dirichlet', 'solve_dirichlet_sparse', 'lava_room']

import numpy as np

from numpy.linalg        import solve
from scipy.sparse        import csr_matrix
from scipy.sparse.linalg import spsolve

from frplib.exceptions import InputError, KindError
from frplib.frps       import frp
from frplib.kinds      import conditional_kind, constant, either, uniform, weighted_as
from frplib.utils      import clone, irange
from frplib.vec_tuples import as_vec_tuple


def solve_dirichlet(cKind, *, fixed, fixed_values, alpha=0, beta=1, states=None):
    """Solves a Dirichlet problem determined by a conditional Kind and boundary constraints.

    Specifically, we want to solve for a function f on the domain of cKind
    that satisfies

       f(s) = fixed_values[i] when s in fixed[i] for some i, and
       f(s) = alpha + beta E(f(cKind(s))) otherwise.

    Parameters
      + cKind: ConditionalKind - determines Kind of transition from each state.
            Its domain is the set of possible states if explicitly available
            and the states parameter is not supplied.  The target values
            of cKind must be a subset of the same set of states.
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
    if states is None:
        if not cKind._has_domain_set:
            raise KindError('solve_dirichlet_sparse cannot deduce state set from cKind')
        states = list(cKind._domain_set)

    for i, fix in enumerate(fixed):
        fixed[i] = set(map(as_vec_tuple, fix))

    fixed_map = {}
    free_map = {}
    free_states = []
    free_index = 0
    for s in states:
        is_free = True
        for i, fix in enumerate(fixed):
            if s in fix:
                fixed_map[s] = fixed_values[i]
                is_free = False
                break
        if is_free:
            free_states.append(s)
            free_map[s] = free_index
            free_index += 1

    data = []
    rhs = []
    for s in free_states:
        row_s = []
        next_states = cKind.target(s)
        rhs_value = alpha

        for t in states:
            v = beta * next_states.kernel(t)
            if t in fixed_map:
                rhs_value += v * fixed_map[t]
            elif t == s:
                row_s.append(1 - v)
            else:
                row_s.append(-v)
        data.append(row_s)
        rhs.append(rhs_value)

    A = np.array(data, dtype=np.float64)
    b = np.array(rhs, dtype=np.float64)
    f_s = solve(A, b)

    def f(*state):
        if len(state) == 1 and isinstance(state[0], tuple):
            s = as_vec_tuple(state[0])  # type: ignore
        else:
            s = as_vec_tuple(state)     # type: ignore
        if s in fixed_map:
            return fixed_map[s]
        return float(f_s[free_map[s]])

    return f

def solve_dirichlet_sparse(cKind, *, fixed, fixed_values, alpha=0, beta=1, states=None):
    """Solves a Dirichlet problem determined by a conditional Kind and boundary constraints.

    This is used for a system where the number of possible transitions in most
    rows is a relatively small portion of the total number of states, enabling
    much more efficient methods to solve the problem.

    Specifically, we want to solve for a function f on the domain of cKind
    that satisfies

       f(s) = fixed_values[i] when s in fixed[i] for some i, and
       f(s) = alpha + beta E(f(cKind.target(s))) otherwise.

    Parameters
      + cKind: ConditionalKind - determines Kind of transition from each state.
            Its domain is the set of possible states if explicitly available
            and the states parameter is not supplied. The target values
            of cKind must be a subset of the same set of states.
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
    if states is None:
        if not cKind._has_domain_set:
            raise KindError('solve_dirichlet_sparse cannot deduce state set from cKind')
        states = list(cKind._domain_set)

    for i, fix in enumerate(fixed):
        fixed[i] = set(map(as_vec_tuple, fix))

    fixed_map = {}
    free_map = {}
    free_states = []
    free_index = 0
    for s in states:
        is_free = True
        for i, fix in enumerate(fixed):
            if s in fix:
                fixed_map[s] = fixed_values[i]
                is_free = False
                break
        if is_free:
            free_states.append(s)
            free_map[s] = free_index
            free_index += 1

    row_indices = []
    col_indices = []
    data = []
    rhs = []
    for s in free_states:
        next_states = cKind.target(s).weights
        row_ind = free_map[s]
        diagonal_done = False

        rhs_value = alpha
        for s_prime in next_states:
            v = beta * float(next_states[s_prime])
            if s_prime in fixed_map:
                rhs_value += v * fixed_map[s_prime]
            elif s_prime == s:
                row_indices.append(row_ind)
                col_indices.append(row_ind)
                data.append(1 - v)
                diagonal_done = True
            else:
                row_indices.append(row_ind)
                col_indices.append(free_map[s_prime])
                data.append(-v)

        if not diagonal_done:
            row_indices.append(row_ind)
            col_indices.append(row_ind)
            data.append(1.0)

        rhs.append(rhs_value)

    n = len(free_states)
    A = csr_matrix((data, (row_indices, col_indices)), shape=(n, n), dtype=np.float64)
    b = np.array(rhs, dtype=np.float64)
    f_s = spsolve(A, b)

    def f(*state):
        if len(state) == 1 and isinstance(state[0], tuple):
            s = as_vec_tuple(state[0])  # type: ignore
        else:
            s = as_vec_tuple(state)     # type: ignore
        if s in fixed_map:
            return fixed_map[s]
        return float(f_s[free_map[s]])

    return f


# Example System in Text

class LavaRoom:
    'A room filled with lava and cool water arranged on a regular grid'

    def __init__(self):
        cells = [(x, y) for y in irange(-6, 6) for x in irange(-12, 12)]

        self.states = cells
        self.lava = {
            (x, y) for x, y in cells
            if ((8 <= x <= 12 and -6 <= y <= -5) or (x == 12 and -4 <= y <= -3) or
                (8 <= x <= 12 and y == 1) or (8 <= x < 9 and y == 0) or
                (11 <= x <= 12 and y == 0) or (x == -12 and -6 <= y <= 1) or
                (x == -11 and -6 <= y <= -1) or (x == -10 and y == -6) or
                (x == 6 and -8 <= y <= -7))
        }
        self.water = {
            (x, y) for x, y in cells
            if ((-8 <= x <= -5 and -6 <= y <= -3) or (6 <= x <= 7 and -6 <= y <= -5) or
                (-4 <= x <= 4 and y == 6) or (-1 <= x <= 1 and y == 5) or
                (x == 0 and y == 4))
        }
        self.fixed = [self.lava, self.water]
        # Originally free was a set, but a list is more useful # set(self.states) - self.lava - self.water

        self.free = [(100, 100)] * (len(cells) - len(self.lava) - len(self.water))
        self.state_index: dict[tuple[int, int], int] = {}
        self.free_index: dict[tuple[int, int], int] = {}
        j = 0
        for i, v in enumerate(cells):
            self.state_index[v] = i
            if v not in self.lava and v not in self.water:
                self.free[j] = v
                self.free_index[v] = j
                j += 1

    def _row(self, fcell, fixed_values=(0, 1)):
        "Returns row and RHS of the specified index (free cell index)."
        x, y = self.free[fcell]
        row: list[float] = [0.0] * len(self.free)
        rhs: float = 0

        row[fcell] = 1.0

        if abs(x) == 12 and abs(y) == 6:
            r = 0.5
        elif abs(x) == 12 or abs(y) == 6:
            r = 1.0 / 3.0
        else:
            r = 0.25

        for delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (x + delta[0], y + delta[1])
            if abs(neighbor[0]) > 12 or abs(neighbor[1]) > 6:
                continue
            if neighbor in self.lava:
                rhs += r * fixed_values[0]
            elif neighbor in self.water:
                rhs += r * fixed_values[1]
            else:
                row[self.free_index[neighbor]] = -r

        return (row, rhs)

    @property
    def cKind(self):
        "Returns the associated conditional Kind."
        @conditional_kind
        def cK(state):
            if state in self.lava or state in self.water:
                return constant(state)

            x, y = state

            if x == 12 and y == 6:
                return either( (12, 5), (11, 6) )
            if x == 12 and y == -6:
                return either( (12, -5), (11, -6) )
            if x == -12 and y == 6:
                return either( (-12, 5), (-11, 6) )
            if x == -12 and y == -6:
                return either( (-12, -5), (-11, -6) )
            if x == 12:
                return uniform( (12, y - 1), (12, y + 1), (11, y) )
            if x == -12:
                return uniform( (-12, y - 1), (-12, y + 1), (-11, y) )
            if y == 6:
                return uniform( (x - 1, 6), (x + 1, 6), (x, 5) )
            if y == -6:
                return uniform( (x - 1, -6), (x + 1, -6), (x, -5) )
            return uniform( (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1) )

        return cK

lava_room = LavaRoom()

@conditional_kind
def K_NSEW(tile):
    "Conditional Kind for an unbounded 2-dimensional random walk."
    x, y = tile
    return uniform( (x - 1, y), (x, y - 1), (x, y + 1), (x + 1, y) )
