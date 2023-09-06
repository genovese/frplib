# index_of

```
index_of(value, xs, not_found=-1, *, start=0, stop=sys.maxsize)
```

Returns the index of `value` in `xs`, or `not_found` if none. If xs
is a list or tuple, restrict attention to the slice from start to
stop, exclusive, where start <= stop.

Unlike the standard Python `find`, this does not raise an exception
if a value is not found. The `not_found` argument is set to a
desired or default value to signal that condition.
