# Expectations of Conditional Kinds

A Conditional Kind is a function from values to Kinds, so taking its
expectation gives a function from values to values (expectations).
This is called a *conditional expectation function*.

If `C` is a Conditional Kind of type `m -> m + n`, then `E(C)` is a
function from source values of dimension `m` to the expectation of
the ***target Kind***, which is a value of dimension `n`.
