# Evaluation of Conditional Kinds

Conditional Kinds act as functions that accept
a value and return a Kind. There are two ways
to evaluate Conditional Kinds that are each
useful in different ways.

If `C` is a Conditional Kind of type `m -> m + n`
and `x` is a valid input value (of dimension `m`),
then:

+ `C.target(x)` is the target Kind (of dimension `n`)
  corresponding to source value `x`.

+ `C.joined(x)` is the Kind (of dimension `m + n`)
  obtained from the target Kind by prepending the
  input `x`. This is the Kind that is produced
  by a join when the source has value `x`.

+ `C(x)` returns the same (target) Kind as `C.target(x)`.
