# Constraining Kinds with Observations

## Operators

The `|` operator, pronounced "given", is used to constrain Kinds with an observation.
The Kind goes on the left and a *condition* repreenting the observation goes
on the right. The observation is taken to be that the condition is *true*.

For example, 
```python
    k = uniform((1, 2, 4), (3, 9, 27), (4, 16, 64))
    k | (Proj[3] < 50)
```
The Kind `k | (Proj[3] < 50)` is the constrained version of `k` having
obseved that the third component of its value is less than 50.
If, when `k` is activated, its value satisfies the condition,
the constrained Kind will have the same value.
Otherwise, the constrained Kind samples clones of `k` until the constraint is
satisfied.

The parentheses around the condition are needed because the `|` operator
has low precedence.

Any condition that is compatible with the Kind on the left can be used,
but the condition should be true for *some possible value* of the Kind,
or the computation will not terminate.

In the case where we would like to apply a transform after constraining
with an observation, we can use the `@` operator for the transform
and the condition will remember (and act upon) the original Kind.
For example,
```python
    k = uniform((1, 2, 4), (3, 9, 27), (4, 16, 64))
    Proj[3] @ k | (Proj[1] + Proj[2] % 2 == 0)
```


## Procedures

We use the `given` function on the right side of a `yield` to impose
a conditional constraint. It can take a value that is either True
or `<1>` or False or `<0>`.  This value corresponds to the value of the 
condition on the Kind's value.

For example,
```python
    @kind
    def k_given_sum():
        x = yield k
        yield given(sum(x) < 40)
        return x
```
corresponds to `k | (Sum < 40)`.
