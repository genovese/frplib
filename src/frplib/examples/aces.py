#
# Aces Example in Section 7
#

__all__ = ['between_aces', 'two_four_gaps', 'cut',]

from frplib.statistics import statistic, Id
from frplib.utils      import irange
from frplib.vec_tuples import as_vec_tuple


def _ace_gaps(deck, aces):
    "Computes tuple of gap sizes between specified `aces` in a deck."
    gaps = []
    deck_size = len(deck)
    start = 0
    for pos, card in enumerate(deck):
        if card in aces:
            gaps.append(pos - start)
            start = pos + 1
    gaps.append(deck_size - start)

    return as_vec_tuple(gaps)

@statistic
def between_aces(deck):
    "Returns a tuple of the number of cards between successive aces (including the ends of the deck)."
    return _ace_gaps(deck, {1, 14, 27, 40})   # These *are* the cards we're looking for

@statistic
def two_four_gaps(deck):
    "A simple analogue of between_aces for a deck of five cards and two 'aces'."
    return _ace_gaps(deck, {2, 4})

def cut(ace1, ace2, deck_size=52, aces={1, 14, 27, 40}):
    """A statistic factory that swaps the segments between two aces specified by order.

    Parameters
      ace1: int - ordinal in 1..len(aces)+1 of an ace (len(aces)+1 for end of deck)
      ace2: int - ordinal in 1..len(aces)+1 of another ace (len(aces)+1 for end of deck)
      deck_size: int [=52] - number of cards in the deck 1..deck_size
      aces: set[int] [={1,14,27,40}] - cards in deck corresponding to aces

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
