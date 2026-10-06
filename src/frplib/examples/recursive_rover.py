"""Recursive Rover Example 8.15"""

from frplib.kinds        import Kind, conditional_kind, constant, uniform
from frplib.statistics   import __
from frplib.utils        import iterate


def time_to_base(t: Kind) -> Kind:
    """Returns the conditional kind of time to base.
    Here, t is the *kind* of the remaining time *after the step*.

    """
    base = conditional_kind({1: constant(3),
                             2: t ^ (__ + 5),
                             3: t ^ (__ + 7)})
    channel = uniform(1, 2, 3)

    return base // channel

def run_rover(n_iterations: int) -> Kind:
    return iterate(time_to_base, n_iterations, constant(3))
