# Kind Combinators

## Operators

+ `*` - independent mixtures of kinds
+ `**` - independent mixture power, `k ** n` for kind `k` and natural number `n`
+ `>>` - general mixture of kinds, `k >> m` where `k` is the mixture kind and `m` is a conditional kind.
         Accepts a general dict or function with appropriate values, but using `conditional_kind`
         is recommended.
+ `|` - conditionals, `k | c` is the conditional of the kind `k` given the condition `c`.
    Typically, `c` is a Condition, a type of Statistic that returns a boolean (0-1) value.
+ `//` - conditioning, `m // k` (read "m given k") is equivalent to
  `k >> m ^ Project[-m.dim, -m.dim+1,...,-1]`. This reflects the common operation of *conditioning*,
  with the focus on the conditional kind `m`; it extracts the kind produced by `m` after
  averaging over the possible values of `k`.
+ `@` - evaluate a statistic at a kind with context
   `psi @ k` is equivalent to `psi(k)` except that in a conditional expression
   of the form `psi@k | c` the condition `c` receives the full kind `k` as input
   rather than the value of `psi(k)`. This makes some conditional expressions
   more convenient to enter. If `k` has dimension d, this is equivalent to
   `(k * psi(k)) | c(Proj[:(d+1)]))[(d+1):]`, which is decidedly less friendly.

## Special Functions

+ `bin` :: a kind that bins the values of another kind

+ `fast_mixture_pow` :: efficiently computes `stat(a_kind ** n)` for some statistics.

+ `bayes(observed_y, x, y_given_x)` :: applies Bayes's rule given quantity y having
      observed value `observed_y`, using the kind `x`, conditional kind `y_given_x`.

## Sub-topics

+ `bin`, `fast_mixture_pow`
