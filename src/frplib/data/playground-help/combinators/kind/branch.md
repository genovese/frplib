# branch

`branch` is a Kind combinator that represents a choice
between two Kinds, with a branching point in the tree,
weights those branches, and values for the roots of the subtrees.

Starting in version 3.0.?, Kinds returned by branch default to a RAW
display format. This is because this function is intended as the way
to build Kinds with width > 1 explicitly level by level.

The full signature is
```
    branch(*ks, values=None, weights=None)
```
where `*ks` represents zero or more arguments, all of which are
either Kinds or values, all of that dimension.
Values among `*ks* are automatically converted to constant Kinds with `constant`.

The `values` argument, if supplied, should be a list of values of (at least)
the same length as the number of arguments in `*ks`.
These are the values at the roots of the subtrees after the branching.
If not supplied, these are assigned as 1, 2, ... through however many arguments
are given. It is an error if some but too few `values` are supplied.

The `weights` argument, if supplied, is a list of positive numbers that
are assigned as weights on the edges of the branch point.
If too few weights are given (relative to `*ks`), the last weight supplied
is repeated. If no weights are given, they are all taken as 1.

Examples:
  + `branch(choice(1, 2), choice(2, 3), choice(4, 5), weights=[1, 4, 2])`
    ```
                             ,------ 1 ----- <1, 1>
        ,------ 1 ----- <1> -|
        |                    `------ 1 ----- <1, 2>
        |
        |
        |                    ,------ 1 ----- <2, 2>
    <> -+------ 4 ----- <2> -|
        |                    `------ 1 ----- <2, 3>
        |
        |
        |                    ,------ 1 ----- <3, 4>
        `------ 2 ----- <3> -|
                             `------ 1 ----- <3, 5>
    ```
  
  + `branch(1, 2, 3, 4)` is equivalent to `uniform((1, 1), (2, 2), (3, 3), (4, 4))`
