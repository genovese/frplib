# A Kid Named Florida Example Chapter 0 Section 8

from frplib.statistics  import And, Or, Proj

a_rare_girl = Or(
    And(Proj[1] == 1, Proj[3] == 11),
    And(Proj[2] == 1, Proj[4] == 11)
)
