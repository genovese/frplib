# iterates

Calls a given function on a starting value and then repeatedly calls
the function on the previous value returned.

Returns the first n + 1 items of the sequence: start, f(start), f(f(start)),
f(f(f(start))), ....  If n <= 0, a singleton list containing start is returned.

Extra positional and keyword arguments are passed to f in each call.

The signature is

```
iterates(f, n, start *extra_args, **extra_kwargs)
```

## Parameters

+ f :: a function from A -> A, however f can accept extra positional or keyword
      arguments; these are given by `extra_args` and `extra_kwargs`, respectively.

+ n :: the number of times to iterate; if n <= 0, `[start]` is returned.

+ start :: a value of type A, the initial value of the sequence

+ extra_args :: zero or more additional arguments that are passed to `f`
      following the value of type A.

+ extra_kwargs :: zero or more additional keyword arguments that are passed
      to `f` following the value of type A and `extra_args`.

## Returns

A value of type list[A], containing the first `n + 1` items of the
sequence `start, f(start), f(f(start)), ...`.

## Examples

+ `iterates(lamda x: x + 1, 10, 0) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`
+ `iterates(lambda km: km * k, 9, k)` gives the list of kind `k` through `k ** 10`

## Note

   The function `iterate` returns only the last value of this list
   rather than the list itself.
