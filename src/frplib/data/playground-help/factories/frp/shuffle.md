# shuffle

`shuffle` is an FRP-factory that takes a collection of items
and returns a uniform random shuffle of the given items.
Typically, we expect that the items will be a list of quantities,
which will be components of the FRP's value.
But the function operates somewhat more generally.

Be aware that the Kind of the resulting FRP will be very
slow to compute unless the number of items is very small (< 10).

Examples:

 + `shuffle([1, 2, 3, 4])`
  
    Produces for instance
    ```
        An FRP with value <4, 3, 1, 2>. (It may be slow to evaluate its kind.)
    ```
 
 + `shuffle([symbol('a'), symbol('b'), symbol('c')])`
    Produces for instance 
    ```
         An FRP with value <c, a, b>. (It may be slow to evaluate its kind.)
    ```
 + `shuffle([[1, 2],[2, 3], [3, 4]]) ^ VecTuple.join`

    Produces for instance 
    ```
         An FRP with value <3, 4, 2, 3, 1, 2>. (It may be slow to evaluate its kind.)
    ```
    This last example is a bit of a hack, but it shows you you can shuffle
    groups of items rather tha individual items
