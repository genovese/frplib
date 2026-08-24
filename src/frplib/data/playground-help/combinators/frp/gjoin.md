# General Joins of FRPs

## Operators

The `>>` operator forms a general join of an FRP and conditional FRPs.
`X >> M` is an FRP when `X` is an FRP and `M` is a compatible conditional FRP.
In particular, if `X` has dimension 'd' and `M` has type `d -> n`,
then `X >> M` has dimension `n`.

A conditional FRP represents a mapping from values to FRPs.
It gives a random quantity produced at the next stage when
given a particular value in the current stage.
These are often made with `conditional_frp` as a function or decorator.
See topics under *Conditional FRPs*.

The `//` operator is called the **conditioning operator**.
This is like `>>`, but the arguments are given in the opposite order,
and the result FRP drops the value produced by the source FRP.

Specifically, `M // X` is a transform of `X >> M` by a projection that drops `X`'s value.

## Procedures

Using `X` and `M` as above, we can represent a general join with an FRP procedure.
```python
    @frp
    def X_join_M():
        x = yield X
        y = yield M(x)
        return (x, y)
```
The conditioning operation `M // X` is obtained with a similar procedure:
```python
    @frp
    def X_join_M():
        x = yield X
        y = yield M(x)
        return y
```
which simply projects out the value of `X`.
