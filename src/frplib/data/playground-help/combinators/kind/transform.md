# Transforming a Kind

There are three operators used to transform a Kind by a statistic.

+ `^` :: The transformation operator takes a Kind on the left and a statistic on the right
      and returns the transformed Kind. The advantage of this operator is that the
      statistic can have a complicated expression, as with a statistic factory
      or statistic expression. Note also that this operator can be chained, so
      `k ^ psi1 ^ psi2` first transforms `k` by `psi1` and then transforms the
      resulting Kind by `psi2`.
         
+ `()` :: This is the ordinary evaluation operator that *looks like* a function call
      but is in fact a transform operator. The statistic goes to the left of the
      ()s, and the Kind *inside* the ()s. So, `psi(k)` is the transformed Kind.
      This is equivalent to `k ^ psi`.  This form is most convenient when the
      statistic has a name.

+ `@` :: A special version of `^` that retains memory of the transformed Kind.
      This is used primarily with observations, so that the condition
      after a given bar `|` can operate on the right thing.

      Example: `psi @ k | (full == 2)`.  Here, `full` is a condition that
      acts on the `k` (the "full" Kind) rather than on the transformed
      Kind `psi(k)`. The result is equivalent to `psi(k | (full == 2))`.

In addition, you can transform with a Kind *procedure*.

If `k` is a Kind and `psi` is a compatible statistic,
the Kind `r = psi(k)` can be obtained by a procedure as follows

```python
    @kind
    def r():
        x = yield k
        return psi(x)
```

Note that this defines an **Kind** not a function.  For simple transforms, the
operators are generally more convenient. The advantage of procedures is that
they can concisely express a complex combination of operations.
See topic *Kind Procedures* for more detail.
