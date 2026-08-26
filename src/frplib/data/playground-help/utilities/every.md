# every

`every` applies a function to every element of an iterable collection
and returns true if all the results are 'truthy'. (An `x` is truthy
when `bool(x)` is true.)

The full signature is
```
    every(fn, iterable)
```
where `fn` is a function that can accept every element of
the `iterable` collection.

Examples

+ `every(is_even, [2, 4, 6, 8])` => True
+ `every(is_even, [2, 4, 7, 8])` => False
