# FRPs

An FRP is a device that represents a random quantity
that we can measure or observe while a random system
evolves.

An FRP (eventually) generates a random value (a tuple of numbers)
and once it does that value is fixed for all time.

In `frplib`, an FRP is a distinct type of object with
a variety of methods and operations that apply to it.
We use FRPs to build random systems by combining simpler
FRPs into more complicated ones.

We usually use capitalized names for FRPs.

If `X` is an FRP, then `kind(X)` gives its Kind.
In some cases, an FRP's Kind might be difficult to compute,
and `frplib` will attempt to give you a warning in that case.

Printing an FRP causes it to activate and become observed,
showing you its value. You can also access its value
with `X.value`.

The expectation of a FRP `X` is found with `E(X)`.
