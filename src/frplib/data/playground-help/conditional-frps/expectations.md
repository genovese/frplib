# Expectations of Conditional FRPs

A Conditional FRP is a function from values to FRPs, so taking its
expectation gives a function from values to values (expectations).
This is called a *conditional expectation function*.

If `C` is a Conditional FRP of type `m -> m + n`, then `E(C)` is a
function from source values of dimension `m` to the expectation of
the ***target FRP***, which is a value of dimension `n`.
