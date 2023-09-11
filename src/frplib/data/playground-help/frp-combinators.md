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
+ `@` - evaluate a statistic at an FRP with context
   `psi @ X` is equivalent to `psi(X)` except that in a conditional expression
   of the form `psi@X | c` the condition `c` receives the full FRP `X` as input
   rather than the value of `psi(X)`. This makes some conditional expressions
   more convenient to enter. If `X` has dimension d, this is equivalent to
   `(X * psi(X)) | c(Proj[:(d+1)]))[(d+1):]`, which is decidedly less friendly
   and can be used without calculating the FRPs dimension.
