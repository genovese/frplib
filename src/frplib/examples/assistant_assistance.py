# Assistant Assistance Example Chapter 0 Section 8

from typing              import cast

from frplib.expectations import E
from frplib.kinds        import conditional_kind, constant, permutations_of, uniform
from frplib.statistics   import condition, statistic, ArgMax, ArgMin, Proj
from frplib.utils        import irange
from frplib.vec_tuples   import as_scalar_strict, as_vec_tuple, vec_tuple

# Solution to the problem

def is_success(k):
    "Statistic factory that checks if After-k succeeds given <b,s>."

    @condition
    def succeeded(b, s):
        return b > k and s <= k

    return succeeded

def assistant(n):
    "Returns success probabilities of After-k strategies with `n` applicants."
    assert n >= 1, "at least one applicant is required"

    best = uniform(irange(n))

    @conditional_kind(codim=1)
    def pre_best_position(m):
        if m <= 1:
            return constant(0)
        return uniform(irange(1, m - 1))

    best_pre_best = best >> pre_best_position

    success_probs = [0] * n
    for k in range(n):
        success_probs[k] = E(best_pre_best ^ is_success(k)).raw

    return as_vec_tuple(success_probs)

def best_k(n):
    "Finds the best k and probability for the After-k strategy with n applicants"
    success_probs = assistant(n)
    k_star = as_scalar_strict(ArgMax(success_probs))
    return vec_tuple(k_star, success_probs[k_star])

# Direct approach: Checks that best position and the pre-best position are uniform

@statistic
def best_pre_best_of(v):
    b = cast(int, as_scalar_strict(ArgMin(v)))
    if b == 0:
        return (b + 1, 0)
    return (b + 1, as_scalar_strict(ArgMin(v[:b])) + 1)

def check_best_position(n=7):
    permutations_of(irange(1, 7)) ^ best_pre_best_of ^ Proj[1]

def check_pre_best_position(b, n=7):
    Proj[2] @ (permutations_of(irange(1, 7)) ^ best_pre_best_of) | (Proj[1] == b)
