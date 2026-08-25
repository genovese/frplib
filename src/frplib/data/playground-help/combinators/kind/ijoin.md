# Independent Joins of Kinds

## Operators

The `*` operator is the independent join operator.
For two independent Kinds `k1` and `k2`, the Kind `k1 * k2`
is their independent join.
If `k1` has dimension m and `k2` has dimension n,
then `k1 * k2` has dimension m + n.
If `u` is the value of `k1` and `v` is the value of `k2`,
then `u :: v` is the value of `k1 * k2`,
the concatenation of the two tuples into a larger tuple.

This operation is described in detail in Chapter 4.2 of the text.

Note that using the independent join operation is an assertion that
the Kinds being joined are independent. `frplib` makes an effort to
detect obvious dependencies and raise an error if it finds them, but
this effort is bounded to avoid undesirable computational cost in
routine operation.

The `**` operator gives **independent join Powers**.
`k1 ** n` for Kind `k1` and natural number `n`
is the independent join of `n` clones of `k1`,
always starting with `k1` itself.


## Procedures 

You can easily do independent joins using Kind procedures.
For instance, 
```python
    @kind
    def k1k2k3():
       x = yield k1
       y = yield k2
       z = yield k3
       return (x, y, z)
```
is equivalent to `k1 * k2 * k3`.
One advantage of Kind procedures for this is that they accept Kinds as well as Kinds
on the right side of the yield. So,
```python
    @kind
    def k1k2k3():
       x = yield uniform(1, 2, 3)
       y = yield choice((10, 20), (30, 40))
       z = yield constant(10)
       return (x, y, z)
```
creates Kinds from the Kinds before extracting their values.
See *Kind Procedures* topic for more detail.

## A Helper Function

The function `independent_join` accepts a list of Kinds (or FRPs) and forms their 
independent join.
