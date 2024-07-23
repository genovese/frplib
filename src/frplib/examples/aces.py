#
# Aces Example in Section 7
#

from frplib.frps       import conditional_frp
from frplib.kinds      import Kind, conditional_kind, weighted_as, uniform
from frplib.statistics import statistic
from frplib.utils      import irange
from frplib.vec_tuples import vec_tuple

# ATTN:incomplete

@statistic(name='Simple analogue of between_aces', codim=5, dim=3)
def two_four_gaps(deck):
    targets = {2, 4}  # These *are* the cards we're looking for
    diffs = []
    last_index = -1
    for i, card in enumerate(deck):
        if card in targets:
            diffs.append(i - last_index - 1)
            last_index = i
    diffs.append(len(deck) - last_index - 1)
    return diffs
