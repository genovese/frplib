# A Kid Named Florida Example Chapter 0 Section 8

from frplib.calculate   import substitution
from frplib.kinds       import clean, either, weighted_as
from frplib.statistics  import And, Or, Proj
from frplib.symbolic    import symbol

# Question (a)

at_least_one_girl = Or(Proj[1] == 1, Proj[2] == 1)
both_girls = And(Proj[1] == 1, Proj[2] == 1)
girl = either(0, 1)

outcome_no_names = girl * girl | at_least_one_girl


# Question (b)

a_rare_girl = Or(
    And(Proj[1] == 1, Proj[3] == 11),
    And(Proj[2] == 1, Proj[4] == 11)
)

p = symbol('p')
rare = weighted_as(10, 11, weights=[1 - p, p])
neighbors = girl * girl * rare * rare

outcome = neighbors | a_rare_girl
outcome_zero = clean(substitution(outcome, p=0))
