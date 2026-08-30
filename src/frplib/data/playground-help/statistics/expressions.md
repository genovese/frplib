# Statistic Expressions

Statistics in `frplib` act as both functions and as a special type
of object that provide some extra capabilities. In particular,
statistics can be combined with standard Python operators to make
new statistics and they use the evaluation operator on other
statistics as one way to show composition. Some examples will
clarify this.

```python
    # Sum of the first and fourth components
    Proj[1] + Proj[4]

    # Sum of odd components, with composition in mathematical order
    Sum(Proj[1::2])

    # Sum of odd components, with composition in pipeline order
    Proj[1::2] ^ Sum

    # Absolute value of Sum, again equivalent two composition orders
    Abs(Sum)

    Sum ^ Abs

    # Tests if absolute value of sum is bigger than 10

    Sum ^ Abs ^ (__ > 10)
```

The first example combines the two statistics `Proj[1]` and `Proj[4]` by
adding them together. The sum of two statistics is a new statistic
satisfying
```
 (s1 + s2)(x) = s1(x) + s2(x)
```
and similarly with the other operators. This is just how we talk about
the sum (or difference or product or $\dotsc$) of two functions
in mathematics. Remember that `frplib` statistics return vector tuples
(See *Values and Vector Tuples*.) These add (or subtract or multiply or $\dotsc$)
*componentwise*. So `s1(x) + s2(x)` is the component wise sum of the
tuples returned by `s1` and `s2`.  If those tuples have different
dimensions, it raises an error.

The second example shows that using the evaluation operator `()` of one statistic
on another is just ***composition*** in mathematical order. So
```
 Sum(Proj[1::2])(x) = Sum(Proj[1::2](x))
```
`Sum` *after* `Proj[1::2]`.
(Though it may look like it, this is *not* calling the function `Sum` with
argument `Proj[1::2]`. We are "overloading" the evaluation operator when
both terms are statistics to produce a new statistic -- their composition.)

The transform operator `^` also gives us composition of statistics
in the pipeline order. So `Proj[1::2] ^ Sum` does the projection *then* sum.
Similarly, `Sum ^ Abs` does `Sum` *then* `Abs`.
And  `Sum ^ Abs ^ (__ > 10)` chains the three statistics together:
`Sum` *then* `Abs` *then* test for bigger than 10. This produces a **condition**.

A wide variety of statistics can be defined by using statistic expressions
with `frplib` built-in statistics. But keep in mind that your custom statistics
can participate in these expressions too.
