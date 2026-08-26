# as_numpy

`as_numpy` convert a value (tuple of quantities) to a numpy array.

The full signature is
```python
    as_numpy(v, missing=np.nan)
```

The quantities should be numeric or `nothing`. Any `nothing`s are
converted to `missing` which defaults to numpy's NaN (not a number).
