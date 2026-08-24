# Constraining FRPs with Observations

## Operators

The `|` operator, pronounced "given", is used to constrain FRPs with an observation.
The FRP goes on the left and a *condition* repreenting the observation goes
on the right. The observation is taken to be that the condition is *true*.

For example, 
```python
    X = frp(uniform((1, 2, 4), (3, 9, 27), (4, 16, 64)))
    X | (Proj[3] < 50)
```
The FRP `X | (Proj[3] < 50)` is the constrained version of `X` having
obseved that the third component of its value is less than 50.
If, when `X` is activated, its value satisfies the condition,
the constrained FRP will have the same value.
Otherwise, the constrained FRP samples clones of `X` until the constraint is
satisfied.

The parentheses around the condition are needed because the `|` operator
has low precedence.

Any condition that is compatible with the FRP on the left can be used,
but the condition should be true for *some possible value* of the FRP,
or the computation will not terminate.

In the case where we would like to apply a transform after constraining
with an observation, we can use the `@` operator for the transform
and the condition will remember (and act upon) the original FRP.
For example,
```python
    X = frp(uniform((1, 2, 4), (3, 9, 27), (4, 16, 64)))
    Proj[3] @ X | (Proj[1] + Proj[2] % 2 == 0)
```


## Procedures

We use the `given` function on the right side of a `yield` to impose
a conditional constraint. It can take a value that is either True
or `<1>` or False or `<0>`.  This value corresponds to the value of the 
condition on the FRP's value.

For example,
```python
    @frp
    def X_given_sum():
        x = yield X
        yield given(sum(x) < 40)
        return x
```
corresponds to `X | (Sum < 40)`.
