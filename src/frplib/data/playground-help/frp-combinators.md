# FRP Combinators

## Operators

+ `*` - independent mixtures of FRPs
+ `**` - independent mixture power, `X ** n` for FRP `X` and natural number `n`
+ `>>` - general mixture of FRPs, `X >> M` where `X` is the mixture FRP and `M` is a conditional FRP.
         Accepts a general dict or function with appropriate values, but using `conditional_frp`
         is recommended.
+ `|` - conditionals, `X | c` is the conditional of the FRP `X` given the condition `c`.
    Typically, `c` is a Condition, a type of Statistic that returns a boolean (0-1) value.
+ `//` - conditioning, `M // X` (read "b given a") is equivalent to
  `X >> M ^ Project[-b.dim, -b.dim+1,...,-1]`. This reflects the common operation of *conditioning*,
  with the focus on the conditional FRP `M`; it extracts the FRP produced by `M` after
  averaging over the possible values of `X`.

