"""Aces Example in Chapter 6, Section 1 (Example 6.7)

How many cards occur between successive aces in a shuffled deck?

Exports:

  + BetweenAces - Statistic that finds gaps between successive aces in a shuffle
  + TwoFourGaps - Statistic like BetweenAces for a simpler system
  + cut - Statistic factory that exchanges ace gaps; creates an involution.
  + highlight_aces - A convenience statistic to show aces in shuffles in the playground
  + between_aces - DEPRECATED name for BetweenAces
  + two_four_gaps - DEPRECATED name for TwoFourGaps

"""

__all__ = [
    'shuffled_deck',
    'BetweenAces',
    'TwoFourGaps',
    'cut',
    'highlight_aces',
    'between_aces',   # DEPRECATED
    'two_four_gaps',  # DEPRECATED
]

from collections.abc   import Sequence

from frplib.frps       import frp_factory, shuffle
from frplib.statistics import statistic, statistic_factory, __, ElementOf, ForEach, Id, IfThenElse
from frplib.symbolic   import symbol
from frplib.utils      import irange
from frplib.vec_tuples import as_vec_tuple


@frp_factory
def shuffled_deck():
    """a uniform random shuffle of a standard 52 card deck labeled 1..52."""
    return shuffle(irange(52))

def _ace_gaps(deck: Sequence[int], aces: set[int]):
    """Computes tuple of gap sizes between specified `aces` in a deck.

    The deck is assumed to be a permutation of 1..n for some deck size n,
    and aces should be a set of integers representing which of the
    values in 1..n represent `aces`.

    Returns a VecTuple of dimension len(aces) + 1.

    """
    deck_size = len(deck)
    gaps = []
    start = 0
    for pos, card in enumerate(deck):
        if card in aces:
            gaps.append(pos - start)
            start = pos + 1
    gaps.append(deck_size - start)

    return as_vec_tuple(gaps)

@statistic
def BetweenAces(deck):
    "Returns a tuple of the number of cards between successive aces (including the ends of the deck)."
    return _ace_gaps(deck, {1, 14, 27, 40})   # These *are* the cards we're looking for


@statistic
def TwoFourGaps(deck):
    "A simple analogue of between_aces for a deck of five cards and two 'aces'."
    return _ace_gaps(deck, {2, 4})

between_aces = BetweenAces   # DEPRECATED name
two_four_gaps = TwoFourGaps  # DEPRECATED name

@statistic_factory
def cut(ace1, ace2, deck_size=52, aces=frozenset({1, 14, 27, 40})):
    """swaps the segments between two aces specified by order.

    Parameters
      + ace1: int - ordinal in 1..len(aces)+1 of an ace (len(aces)+1 for end of deck)
      + ace2: int - ordinal in 1..len(aces)+1 of another ace (len(aces)+1 for end of deck)
      + deck_size: int [=52] - number of cards in the deck 1..deck_size
      + aces: Iterable[int] [=frozenset({1,14,27,40})] - cards in deck corresponding to aces
            This is a read-only value.

    Returns a statistic that modifies a deck by swapping the cards
    strictly between ace1 and the previous ace (or beginning of deck)
    and strictly between ace2 and the previous ace (or beginning of deck).
    If ace1 or ace2 is len(aces)+1, the segment after the last ace is used.

    If ace1 and ace2 are not distinct, this is just the identity statistic.

    """
    aces = set(aces)  # ensure we have a set
    end_mark = len(aces) + 1

    if ace1 == ace2:
        return Id
    if ace1 > ace2:
        ace1, ace2 = ace2, ace1

    @statistic
    def do_cut(deck):
        swapped = [0] * deck_size
        ace_pos = [-1] + [pos for pos, card in enumerate(deck) if card in aces] + [deck_size]

        index = 0
        for ace in irange(1, end_mark):
            if ace == ace1:
                ace_cap = ace2
            elif ace == ace2:
                ace_cap = ace1
            else:
                ace_cap = ace

            # Move the segment before the designated ace
            n = ace_pos[ace_cap] - ace_pos[ace_cap - 1] - 1
            swapped[index:(index + n)] = deck[(ace_pos[ace_cap - 1] + 1):ace_pos[ace_cap]]
            index += n

            if ace < end_mark:  # Move the ace also
                swapped[index] = deck[ace_pos[ace]]
                index += 1

        return as_vec_tuple(swapped)

    return do_cut

# A convenient statistic for seeing a shuffle's aces and ace gaps in the playground
highlight_aces = ForEach(IfThenElse(ElementOf({1, 14, 27, 40}), symbol('A'), __))
highlight_aces.name = 'highlight_aces'
highlight_aces.doc = 'highlights aces in a standard deck with a symbol A'
