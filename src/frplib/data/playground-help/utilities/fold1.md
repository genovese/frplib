# fold1

This is like `fold`, except the inputs must be a **non-empty list**,
and the first value of the list is used as the initial accumulator.
Thus, the accumulator is of the type of elements in the list.

The signature is

```
fold1(f, input_list)
```

## Examples

+ `fold1(plus, [1, 2, 3, 4]) == 10`
+ `fold1(times, [1, 2, 3, 4]) == 24`
