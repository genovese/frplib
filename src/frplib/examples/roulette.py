# Roulette Example Chapter 0, Section 2

from frplib.frps         import frp
from frplib.kinds        import uniform
from frplib.statistics   import statistic

roulette_spin = uniform(-1, 0, ..., 36)

def roulette(n=1):
    """An interface to FRPs and statistics representing Roulette spins and plays.

    When called as a function, returns an FRP representing n spins (n=1 default)

    ATTN

    """
    return frp(roulette_spin) ** n

setattr(roulette, 'even',
        statistic(
            lambda pocket: 1 if pocket % 2 == 0 and pocket >= 1 and pocket <= 36 else -1,
            dim=1, codim=1
        ))

setattr(roulette, 'straight',
        lambda wins: statistic(
            lambda pocket: 35 if pocket == wins else -1,
            dim=1, codim=1
        ))


# col2 = statistic(lambda pocket: 2 if pocket in set(range(2,36,3)) else -1, codim=1, dim=1)
# corner25 = statistic(lambda pocket: 8 if pocket in set(25,26,28,29) else -1, codim=1, dim=1)
