"""Hello, World example from Chapter 1 in the text.

Defines

+ Three arbitrary FRPs  X, T, and V
+ The `patterned_sequence` function to play with patterned arguments
      to Kind factories.
+ The coin_flips object for studying the Coin Flip example in Section 1.4.

"""
from frplib.frps       import frp
from frplib.kinds      import choice, conditional_kind, uniform, evenly_spaced, sequence_of_values
from frplib.statistics import statistic
from frplib.symbolic   import symbol

__all__= [
    'X', 'T', 'V',
    'patterned_sequence',
    'coin_flips',
]


X = frp(uniform(1, 2, ..., 10))
T = frp(evenly_spaced(0, 10, 101) ** 2)
V = frp(choice(0, 1) * uniform(1, 3, 5, 7, 9) ** 3 * uniform(-4, -2, 0) * uniform(6, 8, 10) ** 2)

def patterned_sequence(*args, **kwds):
    """Generates sequences of numbers following patterns like many built-in Kind factories do."""
    return sequence_of_values(*args, **kwds)


class CoinFlips:
    """A demonstration class for the coin flips example in Chapter 1 of the text."""

    HEADS = symbol('H')
    TAILS = symbol('T')

    def symbolic(self, g=1, s=1, return_kind=False):
        """Returns the symbolic Data FRP or its Kind in the coin flip example of Chapter 1.

        Parameters
        ----------
        g - the ratio of weights heads/tails for the gold coin [default 1]
        s - the ratio of weights heads/tails for the silver coin [default 1]
        return_kind - if True, return the Data Kind, else the Data FRP [default False]

        """
        flip1 = choice(self.TAILS, self.HEADS, g)
        flip2_given_1 = conditional_kind({
            self.TAILS: choice(self.TAILS, self.HEADS, s),
            self.HEADS: choice(self.TAILS, self.HEADS, g),
        })

        c = flip1 >> flip2_given_1

        if return_kind:
            return c
        return frp(c)

    def numeric(self, g=1, s=1, return_kind=False):
        """Returns the numeric Data FRP or its Kind in the coin flip example of Chapter 1.

        Parameters
        ----------
        g - the ratio of weights heads/tails for the gold coin [default 1]
        s - the ratio of weights heads/tails for the silver coin [default 1]
        return_kind - if True, return the Data Kind, else the Data FRP [default False]

        """
        flip1 = choice(0, 1, g)
        flip2_given_1 = conditional_kind({
            0: choice(0, 1, s),
            1: choice(0, 1, g),
        })

        c = flip1 >> flip2_given_1

        if return_kind:
            return c
        return frp(c)

    @statistic
    @staticmethod
    def count_heads(v):
        """Counts the heads in its input tuple, either 1s or symbolic H's."""
        cnt = 0
        for x in v:
            if x in (1, CoinFlips.HEADS):
                cnt += 1
        return cnt

    @statistic
    @staticmethod
    def count_tails(v):
        """Counts the tails in its input tuple, either 0s or symbolic T's."""
        cnt = 0
        for x in v:
            if x in (0, CoinFlips.TAILS):
                cnt += 1
        return cnt

    @statistic
    @staticmethod
    def count_gold(v):
        """Counts the gold coins in its input tuple, numeric or symbolic."""
        cnt = 0
        ind = 0
        while ind < len(v):
            if v[ind] in (1, CoinFlips.HEADS):
                cnt += 2
            else:
                cnt += 1
            ind += 2
        return cnt

    def repeated(self, n, g=1, s=1):
        """Returns a numeric FRP representing `n` repetitions of the coin flip system (2n flips)."""
        return self.numeric(g, s) ** n


coin_flips = CoinFlips()
