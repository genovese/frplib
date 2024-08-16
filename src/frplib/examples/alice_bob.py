#
# Alice and Bob Example as described in the text Ch 0, Sec 6
#

from frplib.frps       import conditional_frp
from frplib.kinds      import Kind, conditional_kind, weighted_as, uniform
from frplib.statistics import MonoidalStatistic
from frplib.utils      import irange
from frplib.vec_tuples import vec_tuple


# The kind of Alice's order, see Figure 17

kindA = weighted_as({
    vec_tuple(0, 0, -20): '0.025',
    vec_tuple(0, 0, -10): '0.025',
    vec_tuple(0, 1, -1):  '0.225',
    vec_tuple(0, 1,  1):  '0.225',
    vec_tuple(1, 0, -2):  '0.225',
    vec_tuple(1, 0,  0):  '0.225',
    vec_tuple(1, 1, 5):   '0.025',
    vec_tuple(1, 1, 10):  '0.025',
})

# Alice and Bob's Trick for Computing Kinds

def monoid_trick(monstat: MonoidalStatistic, k: Kind, n: int) -> Kind:
    """Applies Alice and Bob's trick to compute the kind of
       monstat(k ** n), for a Monoidal Statistic monstat.

    """
    if n == 0:
        return Kind.empty
    if n == 1:
        return k

    kn2 = monoid_trick(monstat, k, (n // 2))

    if n % 2 == 0:
        return monstat(kn2 * kn2)
    return monstat(k * monstat(kn2 * kn2))


# Card Example

def card(n):
    "Returns the conditional kind for the nth card drawn or kind of the first card if n is 1."
    if n == 1:
        return uniform(1, 2, ..., 52)

    def draw_kind(previous_cards):
        next_cards = list( irange(1, 52, exclude=set(previous_cards)) )
        return uniform(next_cards)

    return conditional_kind(draw_kind)

def draw(n):
    "Returns a conditional FRP for the nth card drawn."
    return conditional_frp(card(n))
