# Statistics Combinators

Statistics combinators take one or more statistics and combine
them into a new statistic.

## Component Combinators

+ `ForEach` :: apply a given statistic to every component of a value,
    so  `ForEach(s)` maps `<v1, v2, ..., vn>` to `<s(v1), s(v2), ..., s(vn)>`,
    where the results of the statistics are concatenated into
    a single tuple.
    If `s` is a constant, it is automatically wrapped in `Constantly`.

+ `Fork` :: `Fork(s1, s2, s3, ..., sn)` takes an input value v
    and produces the tuple `<s1(v), s2(v), s3(v), ..., sn(v)>`,
    where the results of the statistics are concatenated into
    a single tuple.
    If `si` is a constant, it is automatically wrapped in `Constantly`,
    so `Fork(Id, 1, s1, s2)` takes `v` to `<v, 1, s1(v), s2(v)>`.

+ `IfThenElse` :: takes three statistics, the first typically a condition.
   If the first is true, apply the second; else apply the third.

   Example: `IfThenElse(__ % 2 == 0, __ // 2, 1 + __ // 2)` operates differently
   on even and odd inputs.

+ `Keep` :: Creates a statistic keeps the components of its input that satisfy
           a given condition. By default, results are padded out to the appropriate
           dimension.

+ `MaybeMap` :: Creates a statistic like a combination of `ForEach` and `Keep`.
           Applies a statistic to each component and joins the results into a
           single tuple, but if the statistic returns `nothing` (a scalar or 1-dim tuple),
           that value is excluded. By default, this pads the result to a common dimension
           inferred from the statistic.

+ `MFork` is exactly like `Fork` but is designed to accept only
   monoidal statistics. It's primary use is in the construction
   of fast mixture powers. (See topic `kind-combinators::fast_mixture_pow`.)
   This is deprecated as `Fork` now auto-detects if it is given
   all monoidal statistics.

## Logical Combinators

+ `And` :: the short-circuiting logical **and** of one or more statistics

+ `Or` :: the short-circuiting logical **not** of one or more statistics

+ `Not` :: produces the logical complement of the given statistic

+ `Xor` :: the logical exclusive or of its arguments (exactly one must be true);
    not short-circuiting

+ `All` :: condition that returns true if all components of its input
   satisfy the given condition
   
+ `Any` :: condition that returns true if any components of its input
   satisfy the given condition
