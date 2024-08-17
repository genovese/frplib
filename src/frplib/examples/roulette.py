# Roulette Example Chapter 0, Section 2

__all__ = ['roulette']

from frplib.exceptions   import IndexingError
from frplib.frps         import frp
from frplib.kinds        import uniform
from frplib.statistics   import statistic

ROULETTE_SPIN = uniform(-1, 0, ..., 36)

RED_SQUARES = set([1, 3, 5, 7, 9, 12, 14, 16, 18,
                   19, 21, 23, 25, 27, 30, 32, 34, 36])

#
# Plays
#

# Even-Money Plays

@statistic(dim=1, codim=1)
def _roulette_even(pocket):
    "Play on all even pockets."
    if pocket % 2 == 0 and pocket >= 1 and pocket <= 36:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_odd(pocket):
    "Play on all odd pockets."
    if pocket % 2 == 1 and pocket >= 1 and pocket <= 36:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_red(pocket):
    "Play on all red pockets."
    if pocket in RED_SQUARES and pocket >= 1 and pocket <= 36:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_black(pocket):
    "Play on all black pockets."
    if pocket not in RED_SQUARES and pocket >= 1 and pocket <= 36:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_first18(pocket):
    "Play on first 18 consecutive pockets 1..18."
    if pocket >= 1 and pocket <= 18:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_second18(pocket):
    "Play on second 18 consecutive pockets 19..36."
    if pocket >= 19 and pocket <= 36:
        return 1
    return -1

# 2-to-1 Plays

def _roulette_dozen(which):
    "Dozen play on twelve consecutive pockets in 1..36, specified by 1, 2, or 3, first, second, third ...."
    if which in [1, 2, 3]:
        which_dozen = which - 1
    elif isinstance(which, str):
        doz = which.lower()
        if doz in ['1', 'first', '1st']:
            which_dozen = 0
        elif doz in ['2', 'second', '2nd']:
            which_dozen = 1
        elif doz in ['3', 'third', '3rd']:
            which_dozen = 2
        else:
            raise IndexingError(f'Invalid Dozen play specifier: {which}. Try 1, 2, or 3 or first, second, or third.')
    else:
        raise IndexingError(f'Invalid Dozen play specifier {which}. Try 1, 2, or 3 or first, second, or third.')

    @statistic(dim=1, codim=1)
    def dozen_play(pocket):
        if which_dozen * 12 < pocket <= (which_dozen + 1) * 12:
            return 2
        return -1

    return dozen_play

def _roulette_column(which):
    "Column play on twelve pockets in one `column`, specified by 1, 2, or 3, first, second, third ...."
    if which == 3:
        which_column = 0
    elif which == 1 or which == 2:
        which_column = which
    elif isinstance(which, str):
        col = which.lower()
        if col in ['1', 'first', '1st']:
            which_column = 1
        elif col in ['2', 'second', '2nd']:
            which_column = 2
        elif col in ['3', 'third', '3rd']:
            which_column = 0
        else:
            raise IndexingError(f'Invalid Column play specifier: {which}. Try 1, 2, or 3 or first, second, or third.')
    else:
        raise IndexingError(f'Invalid Column play specifier {which}. Try 1, 2, or 3 or first, second, or third.')

    @statistic(dim=1, codim=1)
    def column_play(pocket):
        if 1 <= pocket <= 36 and pocket % 3 == which_column:
            return 2
        return -1

    return column_play

# Line Plays

def _roulette_six_line(first_row):
    "Six Line play on six pockets in two adjaced `rows`, specified by any pocket in smallest row."
    if not isinstance(first_row, int) or first_row < 1 or first_row > 36:
        raise IndexingError(f'Invalid pocket {first_row} to specify Six Line play, should be in 1..36.')

    @statistic(dim=1, codim=1)
    def six_line(pocket):
        start = 3 * ((first_row - 1) // 3)
        if start < pocket <= start + 6:
            return 5
        return -1

    return six_line

@statistic(dim=1, codim=1)
def _roulette_top_line(pocket):
    ""
    if pocket <= 3:
        return 6
    return -1

# Other Plays

def _roulette_corner(smallest):
    "Corner play specified by smallest square among four sharing a corner."
    if not isinstance(smallest, int) or smallest < 1 or smallest > 36:
        raise IndexingError(f'Invalid pocket {smallest} to specify Corner play. '
                            f'It should be the smallest square in 1..36 among four that share a corner.')

    winners = set([smallest, smallest + 1, smallest + 3, smallest + 4])

    @statistic(dim=1, codim=1)
    def corner(pocket):
        if pocket in winners:
            return 8
        return -1

    return corner

def _roulette_street(first_row):
    "Street play on three pockets in one `row` specified by any pocket in the row."
    if not isinstance(first_row, int) or first_row < 1 or first_row > 36:
        raise IndexingError(f'Invalid pocket {first_row} to specify Six Line play, should be in 1..36.')

    @statistic(dim=1, codim=1)
    def street(pocket):
        start = 3 * ((first_row - 1) // 3)
        if start < pocket <= start + 3:
            return 11
        return -1

    return street

def _roulette_split(first, second):
    "Split play on two adjacent pockets in -1, 0, 1..36, the first smaller than the second."
    if first < second and (second - first == 1 or second - first == 3
                           or (first == -1 and second in [0, 2, 3])
                           or (first == 0 and second in [1, 2])):

        @statistic(dim=1, codim=1)
        def split(pocket):
            if pocket == first or pocket == second:
                return 17
            return -1

        return split

    raise IndexingError(f'Invalid pair to specify a Split play {(first, second)}. '
                        f'they need to be adjacent with first < second.')

def _roulette_straight(wins):
    "Straight play on the specified pocket in -1, 0, 1..36."
    if not isinstance(wins, int) or wins < -1 or wins > 36:
        raise IndexingError(f'Invalid pocket {wins} to specify a straight play, should be in -1, 0, 1..36.')

    @statistic(dim=1, codim=1)
    def straight(pocket):
        if pocket == wins:
            return 35
        return -1

    return straight


#
# Entry Point
#

def roulette(n=1):
    """An interface to FRPs and statistics representing Roulette spins and plays.

    When called as a function, returns an FRP representing n spins (n=1 default).

    roulette.plays is a list of available standard plays that are available
    as statistics or statistic factories. For instance, roulette.even
    is the Even play and roulette.straight(20) is the Straight play on
    pocket 20.

    """
    return frp(ROULETTE_SPIN) ** n

setattr(roulette, 'plays',
        [
            'even', 'odd', 'red', 'black', 'first18', 'second18',
            'dozen', 'column', 'six_line', 'top_line',
            'corner', 'street', 'split', 'straight',
        ])

setattr(roulette, 'kind', ROULETTE_SPIN)

# Even-Money Plays

setattr(roulette, 'even',     _roulette_even)
setattr(roulette, 'odd',      _roulette_odd)
setattr(roulette, 'red',      _roulette_red)
setattr(roulette, 'black',    _roulette_black)
setattr(roulette, 'first18',  _roulette_first18)
setattr(roulette, 'second18', _roulette_second18)

# 2-to-1 Plays

setattr(roulette, 'dozen',  _roulette_dozen)
setattr(roulette, 'column', _roulette_column)

# Line Plays

setattr(roulette, 'six_line', _roulette_six_line)
setattr(roulette, 'top_line', _roulette_top_line)

# Other Plays

setattr(roulette, 'corner',   _roulette_corner)
setattr(roulette, 'street',   _roulette_street)
setattr(roulette, 'split',    _roulette_split)
setattr(roulette, 'straight', _roulette_straight)
