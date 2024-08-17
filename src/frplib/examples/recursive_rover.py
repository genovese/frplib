# Recursive Rover Example from Chapter 0 Section 8

from frplib.kinds        import conditional_kind, constant, uniform
from frplib.statistics   import __


def time_to_base(t):
    """Returns the conditional kind of time to base.
    Here, t is the *kind* of the remaining time *after the step*.

    """
    base = conditional_kind({1: constant(3),   # type: ignore
                             2: t ^ (__ + 5),
                             3: t ^ (__ + 7)})
    channel = uniform(1, 2, 3)

    return base // channel
