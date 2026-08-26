# compose

`compose(f1, f2, f3, ..., fn)` returns a new function that composes
the specified functions successively.

The composition order is the mathematical order. Specifically,
`compose(f,g)` calls `f` *after* `g`. The outputs of `g` should be
valid inputs to `f`, and similarly for any list of functions. This
is not checked, however.
