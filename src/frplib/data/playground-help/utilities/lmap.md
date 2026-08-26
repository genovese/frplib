# lmap

`lmap` applies a function to every element of an iterable collection
and gathers the results into a list.

The full signature is
```
    lmap(fn, iterable)
```
where `fn` is a function that can accept every element of
the `iterable` collection.

Examples

+ `lmap(int, ['4', '10', '9'])` => `[4, 10, 9]`
+ `lmap(lambda x: x + 1, [4, 10, 9])` => `[5, 11, 10]`

