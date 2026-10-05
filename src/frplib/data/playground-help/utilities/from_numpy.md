# from_numpy

`from_numpy(arr)` converts a 1-dimensional numpy array to a vector tuple of quantities.

There is also a `vec_tuples.from_numpy`, not imported by default
into the playground, that gives more control over the conversion.
Its full signature is
```python
    from_numpy(x: NDArray, convert=None)
```
The components of the returned tuple are native types. If `convert`
is supplied, a more general conversion can be done. It should be a
function that takes an iterable and returns a vector tuple.
