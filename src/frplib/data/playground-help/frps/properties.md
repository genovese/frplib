# Examining Properties of FRPs

If `X` is an FRP, then we can query its various properties with several builtin functions.

## Property Accessors

+ `dim` :: `dim(X)` returns the dimension of `X`, if available. Note that taking
      the dimension of an FRP may force the Kind or value computation.

+ `codim` :: `codim(X)` returns the codimension of `x`, which will always be 0 for an FRP.

+ `size` :: `size(X)` returns the size of `kind(X)`, forcing the computation of the Kind.

+ `typeof` :: `typeof(x)` returns the type `codim -> dim` of an FRP.

## Kinds

+ `kind` :: `kind(X)` returns the Kind of `X`. In most cases, this is already computed,
     but in some complex calculations the Kind can be slow to compute. This forces
     that computation.
