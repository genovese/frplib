# integers

A Kind factory that represents a choice over integer values from `start` to `stop` by `step`.
The full signature is
```python
    integers(start, stop=None, step=1, weight_fn=const(1))
```
If `stop` is None, then the values go from 0 up to `start` by `step`. Otherwise, the values
go from `start` up to but not including `stop`.

`start`, `stop`, and `step` must be integers, as the function name implies.

The `weight_fn` argument (default the constant 1) should be a function; it is
applied to each integer to determine the weights.

Examples

+ `integers(10)` => equivalent to `uniform(0, 1, ..., 9)`
+ `integers(44, 64, 4, weight_fn=lambda x: x // 4)` => is equivalent
  to `weighted_as(44, 48, ..., 64, weights=[11, 12, 13, 14, 15, 16])`
+ `integers(44, 64, 4, weight_fn=lambda x: x // 4)` => is equivalent
  to `weighted_by(44, 48, ..., 64, weights=lambda x: x // 4)`
