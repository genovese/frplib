# Doubled Cards Example, Chapter 0 Section 8

from frplib.frps         import frp
from frplib.kinds        import conditional_kind, uniform, ordered_samples
from frplib.statistics   import Or, Proj
from frplib.utils        import irange


first_card = uniform(1, 2, ..., 100)
all_cards = first_card.values
second_card = conditional_kind({
    first: uniform(all_cards - {first}) for first in all_cards
})

# The Kind of the drawn pair of cards
draw = first_card >> second_card
draw_alt = ordered_samples(2, irange(1, 100))

# Conditions that test for our desired outcomes
is_card_doubled = Proj[2] == 2 * Proj[1]
is_either_doubled = Or(is_card_doubled, Proj[1] == 2 * Proj[2])

# Relevant FRPs and Kinds
P = frp(draw)
D = is_card_doubled(P)
T = is_either_doubled(P)

D_kind = is_card_doubled(draw)     # same as kind(D)
T_kind = is_either_doubled(draw)   # same as kind(T)
