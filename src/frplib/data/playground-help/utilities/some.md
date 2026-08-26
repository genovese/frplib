# some

`some` applies a function to every element of an iterable collection
and returns true if at least one of the results is 'truthy'. (An `x`
is truthy when `bool(x)` is true.)

The full signature is
```
    some(fn, iterable)
```
where `fn` is a function that can accept every element of
the `iterable` collection.

Examples

+ `some(is_even, [2, 4, 7, 8])` => True
+ `some(is_even, [-1, 1, 7, 9])` => False
