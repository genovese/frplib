# `as_quant_vec`

`as_quant_vec(x)` converts `x` into a vector tuple of quantities,
where `x` is an iterable, number, symbol, string, or `nothing`.

It accepts a `convert` function argument that is applied to every
component of the vector tuple. The full signature is
```
    as_quant_vec(x, convert=f)
```
