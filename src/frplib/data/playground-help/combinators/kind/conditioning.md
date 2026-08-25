# Conditioning with Kinds

## Operators

The `//` operator is called the **conditioning operator**.
This is like `>>`, but the arguments are given in the opposite order,
and the resulting Kind drops the value produced by the source Kind.

Specifically, `m // k` is a transform of `k >> m` by a projection that drops `k`'s values.
Here, `k` is a Kind and `m` a conditional Kind.

## Procedures

The conditioning operation `m // k` is equivalent to a Kind procedure:
```python
    @kind
    def k_join_m():
        x = yield k
        y = yield m(x)
        return y
```
which simply projects out the values from `k`.  Note that `m(x)` is the Kind
produced by `m` that corresponds to the value of `m` when it is available.
