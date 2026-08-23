# States of an FRP

An FRP can be in three states: fresh, activated, and observed.

When it is fresh it has not yet produced a value.
When it is activated, it has produced a value, but we have not seen what it is.
And when it is observed, it has produced a value that has been revealed.

If `X` is an FRP, you can tell if it is fresh with `X.is_fresh`,
which will return True or False.
If it is not fresh, it has been activated.
If it has been activated and you have seen the value, it has been observed.

You can activate a fresh FRP `X` without observing it
with `activate(X)`. 

If you print an FRP, you will see its value. You can also access
that value directly with `X.value`.
