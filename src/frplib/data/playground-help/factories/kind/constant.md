# constant

`constant(a)` returns the kind of an FRP whose value is always `a`.

Examples:
  + `constant(0)` is a Kind with only <0> for a value
  + `constant(1, 2, 3)` is a Kind with only <1, 2, 3> for a value
  + `constant((1, 2, 3))` is a Kind with only <1, 2, 3> for a value
  + `constant(2, 4, ..., 12)` is a Kind with only <2, 4, 6, 8, 10, 12> for a value
