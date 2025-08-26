# Statistics

Statistics are transformations that can applied to FRPs and Kinds.
The statistics are data-processing algorithms, functions that take
as input a value of an FRP/Kind and return as output a value of
possibly different (though consistent) dimension.

The dimension of a statistic is the dimension of the values it
takes as input; the co-dimension is the dimension of the values
it produces as output.

A statistic is **compatible** with an FRP or Kind when their dimensions
match and when the possible values of the FRP/Kind are all legal inputs
to the statistic.

There are several types of Statistics.  

 - Conditions are statistics that return a boolean value (encode as
   0 for false, 1 for true). If a statistic is intended for that use
   (as in conditionals) it is worth creating an explicit condition,
   as that will interoperate nicely with some logical operations.

 - Projection statistics extract components of a tuple; they are created by `Proj`.
 
 - Monoidal Statistics represent calculations that can be parallelized,
   and are valid statistics to use with `fast_mixture_pow`.

See topics *statistic-builtins*, *statistic-factories*, and *statistic-combinators* 
for more examples of statistics and how to use them.
See topic *projections* for more about projection statistics.
