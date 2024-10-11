# Get

Get is a statistic factory that mediates access to a
list/array, dictionary, or other indexable object.

`Get(obj)` returns a statistic whose input is used as a key indexing
`obj`. In basic form, the statistic maps `value` to `obj[value]`. By
default, however, if `value` is a 1-dimensional tuple, it will be
converted to a scalar (unless `scalarize=False`). In addition, you
can pass a `key` function that will transform the value into the
indexing key. This function is the identity by default and so has no
effect.

The call signature is `Get(obj, key=identity, scalarize=True)`
where the parameters are

+ obj - a Python object that can be indexed with []
+ key - a function applied to the input value before
      using it to index the object
+ scalarize [=True] - if True, 1-dimensional inputs are
      converted to scalars automatically before applying
      the key function; if False, they are left as tuples.

Examples:
+ uniform(0, 1, ..., 9) ^ Get(array)  where array
  is a python list with length at least 10
+ uniform(0, 1, ..., 5) ** 2 ^ Get(dictionary) where
  dictionary has 2-dimensional tuples as keys.
+ Get([1, 2, 3])(2) == <3>
+ Get([1, 2, 3], key=lambda n: n // 100)(200) == <3>
+ Get({'r1': (1, 2), 'r2': (11, 12), 'r3': (100, 200)},
      key=lambda n: f'r{n}')(2) == <11, 12>
