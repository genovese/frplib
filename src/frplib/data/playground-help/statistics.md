# Statistics

Statistics are transformations that can applied to FRPs and kinds.
The statistics are data-processing algorithms, functions that take
as input a value of an FRP/kind and return as output a value of
possibly different (though consistent) dimension.

The dimension of a statistic is the dimension of the values it
takes as input; the co-dimension is the dimension of the values
it produces as output.

A statistic is **compatible** with an FRP or kind when their dimensions
match and when the possible values of the FRP/kind are all legal inputs
to the statistic.

There are several types of Statistics.  Conditions are statistics that
return a boolean value (encode as 0 for false, 1 for true).
If a statistic is intended for that use (as in conditionals) it is worth
creating an explicit condition, as that will 

Projection statistics are created by `Proj`,
and Monoidal Statistics represent calculations that can be parallelized.

See topics *statistic-factories* and *statistic-combinators* for more detail.
