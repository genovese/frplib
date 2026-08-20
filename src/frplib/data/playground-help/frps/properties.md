# Examining Properties of FRPs

## Property Accessors

+ `dim` :: `dim(x)` returns the dimension of `x`, if available. Note that taking
      the dimension of an FRP may force the kind computation.

+ `codim` :: `codim(x)` returns the codimension of `x`, if available

+ `size` :: `size(x)` returns the size of `x`, usually a kind, if available

+ `values` :: `values(x)` returns the *set* of `x`'s values, if available; applies to kinds

+ `typeof` :: `typeof(x)` returns the type of a statistic, conditional Kind, conditional FRP

