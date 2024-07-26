# Roulette Example Chapter 0, Section 2

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
    if pocket % 2 == 0 and pocket >= 1 and pocket <= 36:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_odd(pocket):
    if pocket % 2 == 1 and pocket >= 1 and pocket <= 36:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_red(pocket):
    if pocket in RED_SQUARES and pocket >= 1 and pocket <= 36:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_black(pocket):
    if pocket not in RED_SQUARES and pocket >= 1 and pocket <= 36:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_first18(pocket):
    if pocket >= 1 and pocket <= 18:
        return 1
    return -1

@statistic(dim=1, codim=1)
def _roulette_second18(pocket):
    if pocket >= 19 and pocket <= 36:
        return 1
    return -1

# 2-to-1 Plays

def _roulette_dozen(which):
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
    if which == 3:
        which_column = 0
    if which == 1 or which == 2:
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
    if pocket <= 3:
        return 6
    return -1

# Other Plays

def _roulette_corner():
    pass  # ATTN: FIX
# corner25 = statistic(lambda pocket: 8 if pocket in set(25,26,28,29) else -1, codim=1, dim=1)

def _roulette_street(first_row):
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
    if first < second and (second - first == 1 or second - first == 3):

        @statistic(dim=1, codim=1)
        def split(pocket):
            if pocket == first or pocket == second:
                return 17
            return -1

        return split

    raise IndexingError(f'Invalid pair to specify a Split play {(first, second)}. '
                        f'they need to be adjacent with first < second.')

def _roulette_straight(wins):
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

    When called as a function, returns an FRP representing n spins (n=1 default)

    ATTN

    """
    return frp(ROULETTE_SPIN) ** n

setattr(roulette, 'plays',
        ['even', 'odd', 'red', 'black', 'first18', 'second18'])

# Even-Money Plays

setattr(roulette, 'even',      _roulette_even)
setattr(roulette, 'odd',       _roulette_odd)
setattr(roulette, 'red',       _roulette_red)
setattr(roulette, 'black',     _roulette_black)
setattr(roulette, 'first18',   _roulette_first18)
setattr(roulette, 'second18',  _roulette_second18)

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
