# Conditioning with FRPs

## Operators

The `//` operator is called the **conditioning operator**.
This is like `>>`, but the arguments are given in the opposite order,
and the result FRP drops the value produced by the source FRP.

Specifically, `M // X` is a transform of `X >> M` by a projection that drops `X`'s value.

## Procedures

The conditioning operation `M // X` is equivalent to an FRP procedure:
```python
    @frp
    def X_join_M():
        x = yield X
        y = yield M(x)
        return y
```
which simply projects out the value of `X`.  Note that `M(x)` is the FRP
produced by `M` that corresponds to the value of `X` when it is available.
