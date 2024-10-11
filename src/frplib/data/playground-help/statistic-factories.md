# Statistics Factories

+ `statistic` :: Creates a statistic from a function. The function is either passed
    as the first argument or is being defined with `@statistic` used as a decorator.

    Optional arguments include:
    - `name` :: a short name to label this statistic; good to have for nice output
    - `dim` :: a tuple of the form (a, b) meaning to accept from a up to b arguments
        where 0 <= a <= b and b can be infinity. If this is a single integer a,
        the dimension becomes (a, a). If None, frplib attempts to infer the dimension.
    - `codim` :: the codim of the statistic if known, None if unknown.
    - `description` ::  a longer string description of the statistic, shown when
        you use `help()` on the statistic.
    - monoidal :: for monoidal statistics, this is the monoidal unit
    - strict :: if True, then strictly enforce the dim upper bound
    - arg_convert :: If supplied, a function that applies to every input component
          before applying the statistic.

   Note that `statistic`, `condition`, and `scalar_statistic`, when used
   as a decorator are *all lowercase letters*. 

+ `scalar_statistic` :: like `statistic` but forces the codim to
    be 1. Can be used as a factory or a decorator on a function
    definition.
    
+ `condition` :: like `statistic` but creates a special type of statistic
    called a Condition, which returns boolean values. This is good to
    use for statistics that will be used as conditions. Conditional operations
    in other statistics produce Conditions automatically, e.g., `Sum == 8`.
    This can be used as a factory or a decorator.

+ `Constantly(a)` :: returns the statistic that always returns `a`.

     Some statistic combinators, like `Fork`, `ForEach`, and `IfThenElse`
     automatically wrap constant values in `Constantly` to produce a statistic.

+ `Proj` :: Creates projection statistics from list of indices. The indices are **1-indexed**.
            Example: `Proj[2]` is the statistic that extracts the second component of a value.
            See *projections* sub-topic.

+ `Permute` :: Creates a permutation statistic. Accepts a sequence of values (or a single iterable)
            giving the new positions, e.g., `Permute(3, 2, 1)` puts the 3rd component first,
            and the first component third.  (more features are coming soon to this)

+ `Append` :: Creates a statistic that appends one or more values to its input tuple.

+ `Prepend` :: Creates a statistic that prepends one or more values to its input tuple.

+ `ElementOf` :: Creates a condition that tests whether a value belongs to a specified
                 set of values.

+ `Get` :: Creates a statistic that uses its argument as a lookup key in an array/list,
           dictionary, or indexable object. The factory takes the object.

## Sub-topics

projections, Get, Permute
