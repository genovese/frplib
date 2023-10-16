# iterate

Calls a given function on a starting value and then repeatedly calls
the function on the previous value returned.

Returns nth item in the sequence: start, f(start), f(f(start)),
f(f(f(start))), .... If n <= 0, start is returned as is. Extra
positional and keyword arguments are passed to f in each call.

The signature is

```
iterate(f, n, start *extra_args, **extra_kwargs)
```

## Parameters

+ f :: a function from A -> A, however f can accept extra positional or keyword
      arguments; these are given by `extra_args` and `extra_kwargs`, respectively.

+ n :: the number of times to iterate; if n <= 0, `start` is returned as is.

+ start :: a value of type A, the initial value of the sequence

+ extra_args :: zero or more additional arguments that are passed to `f`
      following the value of type A.

+ extra_kwargs :: zero or more additional keyword arguments that are passed
      to `f` following the value of type A and `extra_args`.

## Returns

A value of type A, either `start` or a value returned by `f`.

## Examples

+ `iterate(lamda x: x + 1, 10, 0) == 10`
+ `iterate(lambda km: km * k, 9, k)` gives the kind `k ** 10`
+ `iterate(lambda state: next_state // state, 10, Kind.empty)` conditions the
      conditional kind `next_state` on the kind `state` 10 times.
