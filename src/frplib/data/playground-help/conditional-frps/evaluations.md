# Evaluating Conditional FRPs

Conditional FRPs act as functions that accept
a value and return a FRP. There are two ways
to evaluate Conditional FRPs that are each
useful in different ways.

If `C` is a Conditional FRP of type `m -> m + n`
and `x` is a valid input value (of dimension `m`),
then:

+ `C.target(x)` is the target FRP (of dimension `n`)
  corresponding to source value `x`.

+ `C.joined(x)` is the FRP (of dimension `m + n`)
  obtained from the target FRP by prepending the
  input `x`. This is the FRP that is produced
  by a join when the source has value `x`.

+ `C(x)` returns the same (target) FRP as `C.target(x)`.
