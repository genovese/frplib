# Dirichlet Solutions Example from Section 6

__all__ = ['solve_dirichlet', 'solve_dirichlet_sparse', 'K_NSEW', 'lava_room']

from frplib.exceptions import InputError
from frplib.frps       import frp
from frplib.kinds      import conditional_kind, uniform, weighted_as
from frplib.utils      import clone, irange


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

lava_room = LavaRoom()
