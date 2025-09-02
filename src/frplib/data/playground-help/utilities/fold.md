# fold

Folds an input sequence by successively updating an accumulator
that starts with a given initial value.

The folding function `f` takes two arguments, an accumulator
and an input value (along with optional extra arguments)
and returns an *updated* accumulator. The inputs can
be an arbitrary iterable sequence.

So calling `fold(f, init, inputs, ...)` is equivalent to the following
loop:
```
    acc = init
    for x in inputs:
        acc = f(acc, x, ...)
    return acc
```
The `...` stands in for optional extra arguments and keyword arguments
that are passed to the folding function as is.


The signature is

```
fold(f, init, inputs)
```

## Parameters

+ f :: a function from (A, B) -> A, however f can accept extra positional or keyword
      arguments; these are given by `extra_args` and `extra_kwargs`, respectively.

+ init :: an initial value for the accumulator (type A)

+ inputs :: an iterable sequence of values (of type B)

+ extra_args :: zero or more additional arguments that are passed to `f`

+ extra_kwargs :: zero or more additional keyword arguments that are passed
      to `f` following `extra_args`.

## Returns

The final updated value of the accumulator (value of type A), or `init` if the
input sequence is empty.

## Examples

+ `fold(plus, 0, [1, 2, 3, 4]) == 10`
+ `fold(times, 1, [1, 2, 3, 4]) == 24`


# fold1

This is like `fold`, except the inputs must be a **non-empty list**,
and the first value of the list is used as the initial accumulator.
Thus, the accumulator is of the type of elements in the list.

The signature is

```
fold1(f, input_list)
```
