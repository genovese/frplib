# tup

`tup` wraps its arguments in a quantitative vector.

It accepts either a single iterable argument that should contain the
quantifiables to be included in the tuple *or* one or more
quantifiable arguments that will be the components of the resulting
tuple.

The full signature is
```
    tup(*xs, convert=as_quantity)
```
where `*xs` denotes 0 or more arguments.
The `convert` argument defaults to `as_quantity`. It is applied to
every component during the creation of the tuple.

To combine tuples and quantities into a single tuple, see
`VecTuple.join`.

Examples

+ `tup(1, 2, 3)` => <1, 2, 3>
+ `tup(1)` => <1>
+ `tup('1/2')` => <0.5>
+ `tup()` => <>
+ `tup([10, 20, 30, 40])` => <10, 20, 30, 40>
+ `tup(['10', '20', '30', '40'])` => <10, 20, 30, 40>

