#
# Labyrinth Example as described in the text
#

__all__ = [
    'labyrinth', 'steps', 'from_latest', 'start', 'moves',
    'n_moves', 'theseus_latest', 'nth', 'after_move_n',
    'ever_visited',
]

from collections.abc   import Generator, Iterator
from itertools         import islice
from typing            import TypeVar

from frplib.kinds      import ConditionalKind, conditional_kind, constant, Kind, uniform
from frplib.statistics import statistic
from frplib.vec_tuples import as_numeric_vec


# The Labyrinth

labyrinth: dict[int, list[int]] = {
    0: [1, 3],
    1: [0, 5],
    2: [4, 5],
    3: [0, 12],
    4: [2, 5],
    5: [1, 2, 4],
    6: [5, 7],
    7: [6, 8],
    8: [7, 9],
    9: [8, 10],
    10: [9, 33],
    11: [14, 32],
    12: [3, 17],
    13: [14],
    14: [11, 13],
    15: [16],
    16: [15, 18, 32],
    17: [12, 21, 32],
    18: [16, 19, 32],
    19: [18, 20],
    20: [19],
    21: [17, 22],
    22: [21, 23],
    23: [22, 24],
    24: [23, 26],
    25: [26],
    26: [24, 25, 27],
    27: [26, 28],
    28: [27, 29, 30],
    29: [28, 30],
    30: [28, 29, 31],
    31: [30],
    32: [11, 16, 17, 18],
    33: [33],  # Once we get to the end, we stay there
}


# Individual steps

steps = conditional_kind({
    juncture: uniform(neighbors)                    # type: ignore
    for juncture, neighbors in labyrinth.items()
})

assert isinstance(steps, ConditionalKind)

def from_latest(steps: ConditionalKind):
    def mixture(path):
        latest = path[-1]
        return steps[latest]
    return conditional_kind(mixture, target_dim=1)


# Initial state mixer and state update targets

start = constant(0)
moves = from_latest(steps)


# Multiple Moves

def n_moves(start, moves, n):
    """Makes n moves from start and returns the kind up to that point.

    Warning: This kind grows large with n, so keep n to small values.

    See after_move_n and theseus_latest for a more efficient way to
    look at later moves.

    """
    current = start
    for _ in range(n):
        current = current >> moves
    return current

def theseus_latest(initial: Kind, moves: ConditionalKind) -> Generator:
    """Returns a generator of Theseus's latest move.

    Try, for instance:

      nth(theseus_latest(start, moves), 20)

    which gives the kind of Theseus's position after 20 moves.

    """
    current = initial
    while True:
        yield current
        current = (current >> moves)[2]   # same as moves // current

T = TypeVar('T')

def nth(seq: Iterator[T], n: int) -> T:
    "Extracts the nth item from an iterator."
    return next(islice(seq, n, n + 1))

def after_move_n(n: int, start: Kind, moves: ConditionalKind) -> Kind:
    "The kind of Theseus's state after n moves from start."
    return nth(theseus_latest(start, moves), n)

def ever_visited(n: int):
    """Returns a statistic that extracts the current room and visit counts from Theseus's path.

    Parameter n is the number of rooms, and it is assumed the rooms
    are labeled 0..n-1.

    """
    # convert to current room and binary array 1..n
    @statistic
    def visits(path: tuple[int, ...]) -> tuple[int, ...]:
        rooms = [0] * (n + 1)
        rooms[0] = path[-1]  # current room
        for room in path:
            rooms[1 + room] = 1
        return as_numeric_vec(rooms)
    return visits
