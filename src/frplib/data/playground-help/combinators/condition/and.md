# And

The Python `and` operation works only for Python bools and so cannot
operate on conditions as a combinator.
For that purpose, `frplib` offers the `And` combinator.
Note the case!

If `c1`, `c2`, ..., `cn`, are conditions -- Boolean statistics --
then
```python
    And(c1, c2, ..., cn)
```
gives the condition representing the logical-and of the n specified
conditions. It returns true on an input when *all* the specified
conditions return true on that input. (**Note**: the ... in that
display is not literal, in practice it would be replaced with all
the conditions from `c2` to `cn`.) This is a *short-circuiting* and,
meaning that it will only evaluate the statistics (in order) up to
the first that is false (if any).

Examples

+ `And(__ > 0, __ < 2)` => tests whether *all components* of the input are strictly between 0 and 2
+ `And(Scalar > 0, Scalar < 2)` => tests whether a scalar input is strictly between 0 and 2
+ `And(Proj[2] == 4, Proj[1] > 0, Sum == 10)` => tests whether the second component equals 4,
    the first component is positive, and the sum of all components is 10.
+ `And()` => the condition top that is always true

