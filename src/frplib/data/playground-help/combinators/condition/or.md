# Or

The Python `or` operation works only for Python bools and so cannot
operate on conditions as a combinator. For that purpose, `frplib`
offers the `Or` combinator. Note the case!

If `c1`, `c2`, ..., `cn`, are conditions -- Boolean statistics --
then
```python
    Or(c1, c2, ..., cn)
```
gives the condition representing the logical-or of the n specified
conditions. It returns true on an input when *at least one* of the
specified conditions return true on that input. (**Note**: the ...
in that display is not literal, in practice it would be replaced
with all the conditions from `c2` to `cn`.) This is a
*short-circuiting* or, meaning that it will only evaluate the
statistics (in order) up to the first that is true (if any).

Examples

+ `Or(__ > 0, __ < 2)` => tests whether *all components* of the input are either positive or less than 2.
+ `Or(Scalar > 0, Scalar < 2)` => tests whether a scalar input is either positive or less than 2.
+ `Or(Proj[2] == 4, Proj[1] > 0, Sum == 10)` => tests whether at least one of the following is true: the second component equals 4 or
    the first component is positive or and the sum of all components is 10.
+ `Or()` => the condition top that is always false

