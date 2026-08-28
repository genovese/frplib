# tuple_safe

`tuple_safe(fn, arities=None, convert=as_quant_vec, prepare=as_quant_vec)`
returns a function that can accept a single tuple or multiple individual arguments.

Ensures that the returned function has an `arity` attribute set
to the supplied or computed arity.

If `arities` is `None`, the function analyzes `fn` to try to
determine how many arguments it accepts of what type. If `arities`
is `None` and `fn` accepts only one argument, it is imputed that any
tuple dimension is allowed.

If `strict` is False, the returned function accepts a tuple of dimension
higher than the upper arity. If strict is True, the argument dimension
must fall within the specified range.
