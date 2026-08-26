# Binomial

The `Binomial` computes binomial coefficients.

`Binomial(r, k)` equals
```
      r (r - 1) ... (r - k + 1) / k!
```
It takes a 2-tuple and returns a scalar. The second component must be an integer.

Examples

+ `Binomial(5, 1)` => <5>
+ `Binomial(4, 2)` => <6>
+ `Binomial(5.2, 2)` => <10.92>
+ `Binomial(10, 0)` => <1>
