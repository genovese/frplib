# Joins of Conditional Kinds

There are three join operations that apply to Conditional Kinds.

+ `*` :: The Independent Join

  If `R` and `S` are Conditional Kinds with common input values,
  then `R * S` is the Conditional Kind on the intersection of
  their input values. For each such value `x`, it returns
  the independent join of the targets `R(x) * S(x)`.

+ `>>` :: The General Join

  If `R` and `S` are Conditional Kinds of types `m -> m + n`
  and `m + n -> m + n + p`, then `R >> S` is a Conditional
  Kind of type `m -> m + n + p`.  This applies as well
  and commonly when `m = 0`, i.e., when `R` is a Kind.

+ `//` :: The Conditioning Operator

  If `k` is a Kind and `S` is a compatible Conditional
  (dimension `m` and type `m -> m + n`), then
  `S // k` is equivalent to `(k >> S) ^ Proj[(m+1):]`.
