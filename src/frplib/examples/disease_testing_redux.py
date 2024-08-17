# Disease Testing Redux Example from Chapter 0 Section 8

from frplib.kinds       import bayes, conditional_kind, weighted_as
from frplib.symbolic    import symbol


d = symbol('d')
n = symbol('n')
p = symbol('p')

has_disease = weighted_as(0, 1, weights=[1 - d, d])
test_by_status = conditional_kind({             # type: ignore
    0: weighted_as(0, 1, weights=[n, 1 - n]),
    1: weighted_as(0, 1, weights=[1 - p, p])
})

disease_given_positive = bayes(1, has_disease, test_by_status)
disease_given_negative = bayes(0, has_disease, test_by_status)
