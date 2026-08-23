# Special FRP Methods

## Instance Methods

If `X` is an FRP, the following methods/properties give useful informatoin.

+ `X.is_fresh` returns True if `X` is fresh, False otherwise.

+ `X.entropy()` returns the entropy of `X`

+ `X.expectation` returns the expectation of `X` as a property.
   This gives a high-precision decimal quantity and can be used as is.
   Prefer `E(X)` except in specialize computations.

## Class Methods

The FRP class `FRP` gives access to a few useful tools.

+ `FRP.sample` :: `FRP.sample(n, X)` generates a sample of `n` clonees of `X` and provides
    a tabular summary of the results. You can pass a Kind instead of an FRP in the second
    argument as well. With the `summary=False` argument, this gives the entire sample
    rather than just a summary.
    
+ `FRP.sample1` :: Returns a single sample, equivalent to `FRP.sample(1, X)`. Prefer `clone`.

+ `FRP.activate` :: `FRP.activate(X)` activates `X` and returns it. Generally `activate` is more useful
    as it does not return anything that could be printed inadvertently.
