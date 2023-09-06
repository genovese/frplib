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

## Special Functions

+ `bin` :: a kind that bins the values of another kind

## Sub-topics

+ `bin`
