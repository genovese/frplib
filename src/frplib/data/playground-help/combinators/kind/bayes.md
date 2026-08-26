# bayes - Bayes's Rule

`bayes` is a function that applies Bayes's rules.
Its signature is
```python
    bayes(observed_y, x, y_given_x)
```
where

+ `observed_y` is the value observed for an FRP  `Y`,
+ `x` is the Kind of an FRP `X`, and
+ `y_given_x` is a conditional Kind.

If `U` is the conditional FRP for which `y_given_x` is the conditional Kind,
define `Z = X >> U`. This satisfies
```
    X = Z ^ Proj[:(d+1)]   # the "early" stages of the system's output
    Y = Z ^ Proj[(d+1):]   # the "later" stages of the system's output.
```
And `bayes(observed_y, x, y_given_x)` computes the Kind of
```
    Proj[:(d+1)](Z | (Proj[(d+1):] == observed_y))
```
the early-stage output having observed that the later-stage output
of the system is `observed_y`.
This is just:
```
    Proj[:(d+1)]((x >> y_given_x) | (Proj[(d+1):] == observed_y))
```
which is Bayes's rule.
