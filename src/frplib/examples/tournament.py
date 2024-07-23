# Tournament Example from Chapter 0 Section 8

from frplib.expectations import E
from frplib.frps         import independent_mixture
from frplib.kinds        import Kind, conditional_kind, constant, either
from frplib.quantity     import as_quantity
from frplib.statistics   import __

# The initial state of the system
first_round = constant(1, 8, 4, 5, 2, 7, 3, 6)


# Update the states from one round to the next
@conditional_kind
def next_round(players):
    n = len(players)  # Always a power of 2 here
    k = Kind.empty
    for i in range(0, n, 2):
        r1, r2 = players[i], players[i + 1]
        odds = as_quantity('1.15') ** (r2 - r1)
        k = k * either(r1, r2, odds)
    return k


# The Kinds of the players for subsequent rounds
second_round = next_round // first_round
third_round = next_round // second_round
winner = next_round // third_round


# Answering the main questions
E_winner = E(winner)
E_bottom_half = E(winner ^ (__ > 4))


# Two alternative implementations of next_round
# for illustrative purposes
@conditional_kind
def next_round_alt1(players):
    n = len(players)  # Always a power of 2 here
    b = as_quantity('1.15')

    matches = []
    for i in range(0, n, 2):
        r1, r2 = players[i], players[i + 1]
        odds = b ** (r2 - r1)
        matches.append( either(r1, r2, odds) )
    return independent_mixture(matches)

@conditional_kind
def next_round_alt2(players):
    n = len(players)  # Always a power of 2 here
    b = as_quantity('1.15')

    return independent_mixture(
        either(players[i], players[i + 1], b ** (players[i + 1] - players[i]))
        for i in range(0, n, 2)
    )
