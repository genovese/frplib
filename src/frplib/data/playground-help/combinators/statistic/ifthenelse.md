# IfThenElse

The `IfThenElse` combinator chooses one of two statistics depending on properties
of its input.
It takes a condition and two statistics.
If the condition is true on the input, apply the second to the input and return the result,
else apply the third to the input and return the result.

`v ^ IfThenElse(cond, t, f)` equals `t(v)` if `cond(v)` is true
else it equals `f(v)`.

Examples:

+ `IfThenElse(__ % 2 == 0, __ // 2, 1 + __ // 2)` operates differently
   on even and odd inputs.
