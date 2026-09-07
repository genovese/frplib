# force_unkinded

For an FRP `X`, `force_unkinded(X)` ensures that an FRP is an
unkinded expression.

The primary use case is for evolving systems where the sizes of
the Kinds grow quickly making the computation quite slow even
before it reaches the builtin complexity threshold that prevents
large enough Kinds from being computed when their FRPs are
formed.

If this is used at any stage in evolving a random system,
e.g., with evolve(), subsequent FRPs in that evolution
will also be unkinded.

Example:
```python

Initial = ...     # an FRP
next_stage = ...  # a conditional FRP

evolve(force_unkinded(Initial), next_stage, n)
```
You can also pass `force_unkinded` as the `transform` argument
to `evolve`, but this tends to be overkill.
