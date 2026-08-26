# frequencies

Computes frequencies of the values in some iterable collection.
The full signature is
```
    frequencies(xs, counts_only=False)
```

If `counts_only` is False, returns a dictionary mapping the values to their counts.
Otherwise, returns a tuple of counts in decreasing order.

The items in the collection should be hashable.
