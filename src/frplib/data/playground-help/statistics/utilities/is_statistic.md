# is_statistic

`is_statistic(obj)` returns True if `obj` is an `frplib` statistic (builtin, expression, custom),
else False.

Example

```python
@statistic
def double(x):
    return 2 * x
```

+ `is_statistic(double)` => True
+ `is_statistic(Sum)` => True
+ `is_statistic(Proj[2] + Proj[1] > 3)` => True
+ `is_statistic(Constantly(4))` => True
+ `is_statistic(Constantly)` => False
+ `is_statistic(4)` => False
+ `is_statistic("a statistic")` => False
