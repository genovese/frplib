# Waiting for Heads Example from Chapter 0 Section 8

from frplib.expectations import E
from frplib.kinds        import conditional_kind, constant, weighted_as
from frplib.quantity     import as_quantity
from frplib.statistics   import __
from frplib.symbolic     import symbol
from frplib.utils        import iterate
from frplib.vec_tuples   import as_scalar


def wait_for_heads(remaining_flips, q=symbol('q')):
    """Returns the Kind of the total number of flips to get a head.

    `remaining_flips` is the kind of the additional number of flips
        required after seeing a tails

    `q` is the probability of getting a tails. [Default: symbol('q')]

    """
    # Make sure q is a symbol or high-precision number
    q = as_quantity(q)

    # The kind of the current flip
    flip = weighted_as(0, 1, weights=[q, 1 - q])

    # the kind of the total number of flips given the current flip
    flips_given_current = conditional_kind({  # type: ignore
        0: remaining_flips ^ (__ + 1),
        1: constant(1)
    })

    total_flips = flips_given_current // flip
    return total_flips

def wait_more_than(n, q=symbol('q')):
    "Returns probability of waiting more than n flips for heads; q is the weight on tails."
    wait = iterate(wait_for_heads, n + 1, constant(1), q=q)
    probability = E(wait ^ (__ > n))
    return as_scalar( probability )

def wait_exactly(n, q=symbol('q')):
    "Returns probability of waiting more than n flips for heads; q is the weight on tails."
    wait = iterate(wait_for_heads, n + 2, constant(1), q=q)
    probability = E(wait ^ (__ == n))
    return as_scalar(probability)
