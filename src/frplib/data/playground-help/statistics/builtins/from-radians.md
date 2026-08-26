# FromRadians

The `FromRadians` statistic converts a scalar interpreted in radians
to a scalar interpreted in degrees.  It accepts and returns a scalar tuple
and gives an error for a non-scalar.

Examples
+ `FromRadians(Pi/2)` => <90>
+ `FromRadians(0)` => <0>
+ `FromRadians(Pi)` => <180>
