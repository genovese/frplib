# General Joins of Kinds

## Operators

The `>>` operator forms a general join of a Kind and conditional Kinds.
`k >> m` is a Kind when `k` is a Kind and `m` is a compatible conditional Kind.
In particular, if `k` has dimension 'd' and `m` has type `d -> n`,
then `k >> m` has dimension `n`.

A conditional Kind represents a mapping from values to Kinds.
It gives a random quantity produced at the next stage when
given a particular value in the current stage.
These are often made with `conditional_kind` as a function or decorator.
See topics under *Conditional Kinds*.

The `//` operator is called the **conditioning operator**.
This is like `>>`, but the arguments are given in the opposite order,
and the result Kind drops the value produced by the source Kind.

Specifically, `m // k` is a transform of `k >> m` by a projection that drops `k`'s value.

## Procedures

Using `k` and `m` as above, we can represent a general join with a Kind procedure.
```python
    @kind
    def k_join_m():
        x = yield k
        y = yield m(x)
        return (x, y)
```
The conditioning operation `m // k` is obtained with a similar procedure:
```python
    @kind
    def k_join_m():
        x = yield k
        y = yield m(x)
        return y
```
which simply projects out the value of `k`.
