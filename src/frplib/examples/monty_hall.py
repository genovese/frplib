#
# Monty Hall Example as described in the text
#

from frplib.calculate  import substitute_with
from frplib.kinds      import uniform, arbitrary
from frplib.statistics import condition, Not
from frplib.utils      import identity


# The basic choices in the game, first Monty's then yours.

door_with_prize = uniform(1, 2, 3)
chosen_door = arbitrary(1, 2, 3, names=['l', 'm', 'r'])  # l (ell) might look funny in output


# Statitics used to decide whether you win under a strategy

@condition
def got_prize_door_initially(outcome):
    monty, you = outcome
    return monty == you

didnt_get_prize_door_initially = Not(got_prize_door_initially)    # type: ignore


# The game outcome kind up to but not including the choice of whether to switch

game_outcome = door_with_prize * chosen_door


# The FRP that gives 1 if you win and 0 if you lose is an event.
# The kind of that event is determined by whether you switch
# or don't switch. The following are those kinds.

dont_switch_win = got_prize_door_initially(game_outcome)
switch_win = didnt_get_prize_door_initially(game_outcome)


# Analyze the game for any choice of doors
# The Win kinds are the same for any choice of left/middle/right weights.

def outcome_by_strategy(left=1, middle=1, right=1, *, switch=None):
    """Returns outcome for specified strategy of yours.

    left, middle, right are weights you assign the three doors
      These should be positive numbers

    switch is None (the default), True, or False.
      If switch None, show the game outcome kind for your strategy up
      to but not including your decision to switch. If it is True,
      show the outcome where choose Switch, and if False, the outcome
      where you choose Don't Switch.

    """
    outcome = game_outcome.bimap(identity, substitute_with({'l': left, 'm': middle, 'r': right}))

    if switch is True:
        return got_prize_door_initially(outcome)

    if switch is False:
        return didnt_get_prize_door_initially(outcome)

    return outcome
