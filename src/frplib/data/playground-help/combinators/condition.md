# Condition Combinators

+ `And` :: the short-circuiting logical **and** of one or more statistics

+ `Or` :: the short-circuiting logical **not** of one or more statistics

+ `Not` :: produces the logical complement of the given statistic

+ `Xor` :: the logical exclusive or of its arguments (exactly one must be true);
    not short-circuiting

+ `All` :: condition that returns true if all components of its input
   satisfy the given condition
   
+ `Any` :: condition that returns true if any components of its input
   satisfy the given condition

Note that these logical combinators start with a capital letter. 
The built-in Python operators `and` and `or` *will not work* in statistic expressions,
as Python does not handle custom objects with those operators.
