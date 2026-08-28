# Computing Log-Likelihoods for a Kind

If `x` is a value and `k` is a Kind, then the
likelihood of `x` for the Kind `k` is the canonical
weight of the value `x` or 0 if `x` is not a value.

Notice that this is the same definition as the kernel, but there is
an important conceptual difference. When computing the kernel, the
Kind `k` is fixed, and we vary the values we give it. When computing
the likelihood, the (observed) value `x` is fixed, and we vary the
Kinds we give it. This difference is essential to the distinct way
we use the two functions. Although for the same `x` and `k` they
give the same result, they are fundamentally different as functions.

If `k` is a Kind and `x` is a tuple of `n` values, the ***log
likelihood** of `x` for the Kind `k ** n` can be found by
`k.log_likelihood(x)`. The log-likelihood is the natural log of the
likelihood function for `x` at `k ** n`.

This defines the log-likelihood function for independent
observations from this Kind. It accepts an iterable of n possible
values of this Kind K, which are treated as an observation from
(i.e., a possible value of) the Kind K ** n. This requires a Kind
with numeric weights. (Not currently checked.)

The form of this function may change in future versions to
emphasize that the Kind is the variable here, which does not
come through syntactically in this style.
