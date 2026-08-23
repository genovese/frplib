# Kind Combinators

## Operators

+ `*` - independent joins of Kinds
+ `**` - independent join power, `k ** n` for Kind `k` and natural number `n`
+ `>>` - general join of Kinds, `k >> m` where `k` is the join Kind and `m` is a conditional Kind.
         Accepts a general dict or function with appropriate values, but using `conditional_kind`
         is recommended.
+ `|` - observations, `k | c` is the constrained Kind `k` with the observation `c`.
    Typically, `c` is a Condition, a type of Statistic that returns a boolean (0-1) value.
    The `|` is read 'given'.
+ `//` - conditioning, `m // k` (read "m given k") is equivalent to
  `k >> m ^ Project[-m.dim, -m.dim+1,...,-1]`. This reflects the common operation of *conditioning*,
  with the focus on the conditional Kind `m`; it extracts the Kind produced by `m` after
  averaging over the possible values of `k`.
+ `@` - evaluate a statistic at a Kind with context
   `psi @ k` is equivalent to `psi(k)` except in an observation
   of the form `psi@k | c` the condition `c` receives the full Kind `k` as input
   rather than the value of `psi(k)`. This makes constraining with observations
   more convenient. If `k` has dimension d, this is equivalent to
   `(k * psi(k)) | c(Proj[:(d+1)]))[(d+1):]`, which is decidedly less friendly.

## Special Functions

+ `bin` :: a Kind that bins the values of another Kind

+ `fast_join_pow` :: efficiently computes `stat(a_kind ** n)` for some statistics.

+ `bayes(observed_y, x, y_given_x)` :: applies Bayes's rule given quantity y having
      observed value `observed_y`, using the Kind `x`, conditional Kind `y_given_x`.

## Sub-topics

+ `bin`, `fast_join_pow`
