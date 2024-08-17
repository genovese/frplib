# Rig at Risk Example in Chapter 0 Section 8

from frplib.expectations import E
from frplib.kinds        import conditional_kind, fast_mixture_pow
from frplib.statistics   import Sum

def rig_at_risk(kind_N, kind_D):
    """Computes expectation of total wave damage by mixing kinds then computing E.
    Parameters `kind_N` and `kind_D` give arbitrary kinds for the number of waves
    and the damage per wave.

    """
    @conditional_kind(codim=1)
    def damage_given_n(n):
        return fast_mixture_pow(Sum, kind_D, n)

    return E(damage_given_n // kind_N)
