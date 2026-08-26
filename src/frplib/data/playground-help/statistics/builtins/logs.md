# Log

The `Log`, `Log2`, and `Log10` statistics compute logarithms.
`Log` computes the natural logarithm,
`Log2` computes the logarithm base 2,
`Log10` computes the logarithm base 10.
These accepts a scalar tuple and returns a scalar tuple.
It gives an error when passed an argument with dimension > 1 or dimension 0
or when given a negative argument.

Examples:
+ `Log(1)` => <0>
+ `Log(2.718281828459045235360287471)` => <0.9999999999999999134157889711>
+ `Log(Exp(1))` => <0.9999999999999999999999999999>
+ `Log2(64)` => <6>
+ `Log10(10000)` => <4>

To compute logs by another base, you can define a custom statistic factory:
```python
   @statistic_factory
   def Log_b(base):
       @statistic(codim=1, dim=1)
       def log_b(x):
           return Log(x) / Log(base)
       return log_b
```
