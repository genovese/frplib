# Vector Tuples

`frplib` uses a specialized type of tuples called Vector Tuples,
represented by the object `VecTuple` in the module `frplib.vec_tuples`.

These are a special case of Python tuples that behave more like
vectors. In particular, you can add, subtract, multiple, divide,
raise them to powers, and other mathematical operations
and the results apply *componentwies*. 

So
```
tup(1, 2, 3) + tup(10, 20, 30)  equals  tup(11, 22, 33)
tup(1, 2, 3) ** tup(8, 4, 2)    equals  tup(1, 16, 9)
```
and so forth. 
In these cases, either both operands must be tuples of the same
dimension *or* one must be a number which is used for every
component of the other tuple.
```
tup(1, 2, 3) + 10   equals  tup(11, 12, 13)
tup(1, 2, 3) ** 3   equals  tup(1, 8, 27)
```
Put another way, when vector tuples and scalars are combined,
the **scalars are extended by repetition** to match the
dimension of the other tuple. For non-scalar tuples,
operating on tuples of different dimension raises an
error.

Comparison of vector tuples is different than for standard Python
tuples, which are ordered lexicographically.

Strict inequalities (< and >) hold if all the components
are ordered by the non-strict comparison (<= or >=)
***and*** at least one component is ordered strictly.
The non-strict comparisons (<=, >=, ==) are true
when all components satisfy the condition.

So, the following are true:
```
   tup(1, 2, 3) < tup(1, 2, 4)
   tup(1, 2, 3) < 3
   tup(1, 2, 3) <= tup(1, 2, 3)
   tup(1, 2, 3) == tup(1, 2, 3)
```
and the following are false
```
   tup(1, 2, 3) < tup(1, 2, 3)
   tup(1, 2, 3) < 1
   tup(1, 2, 3) <= tup(1, 2, 2)
   tup(1, 2, 3) == tup(1, 2, 2)
```
In the case of `tup(1, 2, 3) < 3` for example,
the scalar is extended to match the dimension,
so this is equivalent to `tup(1, 2, 3) < tup(3, 3, 3)`
and because all of these satisfy `<=` and at least
one satifies `<`, the condition is true.

The `!=` operator is the complement of the `==` operator.

To get standard Python tuple comparisons by lexicographical
order, wrap the vector tuples in `tuple()`.

## Creating Vector Tuples

+ `tup` is the workhorse for building vector tuples.
  You can pass this multiple individual components
  as separate arguments *or* a single collection
  that gives the components in order.

  Examples:

  - `tup(1, 2, 3, 4)`   => <1, 2, 3, 4>
  - `tup((1, 2, 3, 4))` => <1, 2, 3, 4>
  - `tup([1, f, 3, 4])` => <1, 2, 3, 4>
  
+ `VecTuple.join` 

   Concatenates one or more values in order into a single VecTuple.

   Values can be given as a single iterable argument (not a string)
   containing tuples or scalars, or as multiple tuple or scalar arguments.

   Returns a vector tuple joining all values in order.

   Examples:
   + join(1, 2, 3) => <1, 2, 3>
   + join((1, 2), 3, (4, 5, 6)) => <1, 2, 3, 4, 5, 6>
   + join([(1, 2), (3, 4), (5, 6)]) => <1, 2, 3, 4, 5, 6>


The class for vector tuples is `VecTuple` in module `frplib.vec_tuples`.
