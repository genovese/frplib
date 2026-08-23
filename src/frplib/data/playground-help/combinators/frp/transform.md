# Transforming an FRP

There are three ways to transform an FRP by a statistic.

+ `^` :: The transformation operator takes an FRP on the left and a statistic on the right
      and returns the transformed FRP. The advantage of this operator is that the
      statistic can have a complicated expression, as with a statistic factory
      or statistic expression. Note also that this operator can be chained, so
      `X ^ psi1 ^ psi2` first transforms `X` by `psi1` and then transforms the
      resulting FRP by `psi2`.
         
+ `()` :: This is the ordinary evaluation operator that *looks like* a function call
      but is in fact a transform operator. The statistic goes to the left of the
      ()s, and the FRP *inside* the ()s. So, `psi(X)` is the transformed FRP.
      This is equivalent to `X ^ psi`.  This form is most convenient when the
      statistic has a name.

+ `@` :: A special version of `^` that retains memory of the transformed FRP.
      This is used primarily with observations, so that the condition
      after a given bar `|` can operate on the right thing.

      Example: `psi @ X | (full == 2)`.  Here, `full` is a condition that
      acts on the `X` (the "full" FRP) rather than on the transformed
      FRP `psi(X)`. The result is equivalent to `psi(X | (full == 2))`.
