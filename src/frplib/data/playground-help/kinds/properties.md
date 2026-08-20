# Examining Properties of Kinds




## Property Accessors

These functions work with Kinds, FRPs, Conditional Kinds, and
Conditional FRPs. The `dim` and `codim` functions also work with
Statistics. We specialize the descriptions below to Kinds here.

+ `dim` :: `dim(k)` returns the dimension of `k`

+ `codim` :: `codim(k)` returns the codimension of `k`.  For Kinds, this is always 0.

+ `size` :: `size(k)` returns the size of `k`, the number of possible values of the Kind.

+ `values` :: `values(k)` returns the *set* of `k`'s values. For scalar Kinds, the elements
      are numbers/symbols/nothing (not vector tuples). For the set that always contains
      vector tuples, use the attribute `k.value_set`.

+ `typeof` :: `typeof(k)` returns the type of a Kind, which has the form '0 -> d'
      where d is the dimension of the Kind.
