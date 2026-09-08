"""Example 4.16 `The Drunken Sailor` in Chapter 4 Building with Joins


"""
# pylint: disable=invalid-name, missing-function-docstring

from frplib.frps       import frp, conditional_frp, evolve
from frplib.kinds      import constant, choice, conditional_kind, kind, weighted_as
from frplib.statistics import __, Cases, ElementOf, Fork, Id, Proj
from frplib.utils      import clone, irange

OCEAN = -5
BOAT = 5

# Sailor's starting position on the Dock
D = frp(weighted_as(-2, -1, ..., 2, weights=[0.1, 0.2, 0.4, 0.2, 0.1]))

# The Kind of the FRPs representing each move
move_kind = choice(-1, 1, '2/3')


#
# Modeling the full path
#

def is_valid_path(v):
    """Predicate for a path the sailor might actually take."""
    valid_positions = set(irange(-5, 5))
    return all(x in valid_positions for x in v)

@conditional_frp(domain=is_valid_path, target_dim=1, auto_clone=True)
def S(path):
    """Sailor's path up to the next stage given the path so far."""
    x = path[-1]                      # most recent position
    if x in (OCEAN, BOAT):            # boat or ocean...
        return frp(constant(x))       # ...stay there
    return frp(move_kind ^ (__ + x))  # move left or right

def sailors_paths():
    """Evolve the system through 16 steps keeping the whole path.

    This takes a while as the Kind is quite large.

    Returns a list of several Kinds relating to the path up to
    10 and 16 steps respectively.

    """
    W = D
    for _ in range(10):
        W = W >> clone(S)

    ten_steps = kind(W)
    boat_in_10 = ten_steps ^ Proj[-1]

    sixteen_steps = kind(W >> S >> S >> S >> S >> S >> S)
    boat_in_16 = sixteen_steps ^ Proj[-1]

    # Some transforms to look at
    a = boat_in_10 ^ ElementOf(OCEAN, BOAT)
    b = boat_in_10 ^ Cases({-5: -5, 5: 5}, default=0)

    c = boat_in_16 ^ ElementOf(OCEAN, BOAT)
    d = boat_in_16 ^ Cases({-5: -5, 5: 5}, default=0)

    return [ten_steps, boat_in_10, sixteen_steps, boat_in_16, a, b, c, d]


#
# Refining the state, eschewing the full path
#
# The state becomes the sailor's current position and
# number of steps so far.

@conditional_frp(target_dim=2, auto_clone=True)
def S_n(v):
    """Conditional FRP of the sailor's next state given the current state.

    Here, the state is modeled as (position, steps_so_far).

    """
    x, n = v
    if x in (OCEAN, BOAT):
        return frp(constant(x, n))
    return frp(move_kind ^ Fork(__ + x, n + 1))

@conditional_kind(target_dim=2)
def s_n(x, n):
    """Conditional Kind of the sailor's next state given the current state.

    Here, the state is modeled as (position, steps_so_far).

    """
    if x in (OCEAN, BOAT):
        return constant(x, n)
    return move_kind ^ Fork(__ + x, n + 1)

def sailors_walk(up_to_step, use_kind=False):
    """The state of the sailor's walk after `up_to_step.

    If use_kind is True, use Kinds for the system evolution.
    Otherewise, use FRPs and simulate the system.

    """
    if use_kind:
        initial = kind(D) ^ Fork(Id, 0)
        return evolve(initial, s_n, up_to_step)

    Initial = D ^ Fork(Id, 0)
    return evolve(Initial, S_n, up_to_step)

resolved256 = sailors_walk(256, True) ^ Proj[1] ^ Cases({-5: -5, 5: 5}, default=0)
steps256 = sailors_walk(256, True) ^ Proj[2]
