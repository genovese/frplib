# Independent Joins of FRPs

## Operators

The `*` operator is the independent join operator.
For two independent FRPs `X` and `Y`, the FRP `X * Y`
is their independent join.
If `X` has dimension m and `Y` has dimension n,
then `X * Y` has dimension m + n.
If `u` is the value of `X` and `v` is the value of `Y`,
then `u :: v` is the value of `X * Y`,
the concatenation of the two tuples into a larger tuple.

This operation is described in detail in Chapter 4.2 of the text.

Note that using the independent join operation is an assertion that
the FRPs being joined are independent. `frplib` makes an effort to
detect obvious dependencies and raise an error if it finds them, but
this effort is bounded to avoid undesirable computational cost in
routine operation.

The `**` operator gives **independent join Powers**.
`X ** n` for FRP `X` and natural number `n`
is the independent join of `n` clones of `X`,
always starting with `X` itself.


## Procedures 

You can easily do independent joins using FRP procedures.
For instance, 
```python
    @frp
    def XYZ():
       x = yield X
       y = yield Y
       z = yield Z
       return (x, y, z)
```
is equivalent to `X * Y * Z`.
One advantage of FRP procedures for this is that they accept Kinds as well as FRPs
on the right side of the yield. So,
```python
    @frp
    def XYZ():
       x = yield uniform(1, 2, 3)
       y = yield choice((10, 20), (30, 40))
       z = yield constant(10)
       return (x, y, z)
```
creates FRPs from the Kinds before extracting their values.
See *FRP Procedures* topic for more detail.

## A Helper Function

The function `independent_join` accepts a list of FRPs (or Kinds) and forms their 
independent join.
