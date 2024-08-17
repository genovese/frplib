# Hunter's Success Example in Chapter 0 Sec 8

from random              import random

from frplib.calculate    import substitute_with
from frplib.frps         import independent_mixture
from frplib.kinds        import weighted_as
from frplib.statistics   import Sum
from frplib.symbolic     import symbol, symbols

# Approach #1 in the Text is obtained with the profile expert_plus below

h = symbols('h_0 ... h_7')
hits = [weighted_as(0, 1, weights=[1 - w, w]) for w in h]

all_50_50 = substitute_with(dict(h_0=0.5, h_1=0.5, h_2=0.5, h_3=0.5,
                                 h_4=0.5, h_5=0.5, h_6=0.5, h_7=0.5))
one_expert = substitute_with(dict(h_0=0.1, h_1=0.1, h_2=0.1, h_3=0.1,
                                  h_4=0.1, h_5=0.1, h_6=0.1, h_7=0.9))
expert_plus = substitute_with(dict(h_0=0.1, h_1=0.1, h_2=0.1, h_3=0.1,
                                   h_4=0.1, h_5=0.1, h_6=0.7, h_7=0.9))
some_elders = substitute_with(dict(h_0=0.1, h_1=0.1, h_2=0.1, h_3=0.1,
                                   h_4=0.1, h_5=0.75, h_6=0.75, h_7=0.75))
random_skill = substitute_with({str(w): random() for w in h})

p = symbol('p')
all_equal = substitute_with(dict(h_0=p, h_1=p, h_2=p, h_3=p,
                                 h_4=p, h_5=p, h_6=p, h_7=p))

all_hits = independent_mixture(hits)
number_of_hits = Sum(all_hits)
