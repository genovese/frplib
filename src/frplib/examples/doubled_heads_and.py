# Doubled Heads and Other Patterns Example from Chapter 0 Section 8

from frplib.kinds        import conditional_kind, constant, weighted_as
from frplib.quantity     import as_quantity
from frplib.statistics   import __
from frplib.symbolic     import symbol


def wait_for_2heads(remaining_flips, q=symbol('q')):
    """Returns the kind of the total number of flips to get consecutive heads.

    `remaining_flips` is the kind of the additional number of flips
        required after seeing a tails or heads-tails.

    `q` is the probability of getting a tails. [Default: symbol('q')]

    """
    # Make sure q is a symbol or high-precision number
    q = as_quantity(q)

    # The kind of the current prefix flips
    prefix = weighted_as(0, 2, 3, weights=[q, q * (1 - q), (1 - q) * (1 - q)])

    # the kind of the total number of flips given the current flip
    flips_given_current = conditional_kind({  # type: ignore
        0: remaining_flips ^ (__ + 1),
        2: remaining_flips ^ (__ + 2),
        3: constant(2)
    })

    total_flips = flips_given_current // prefix
    return total_flips
