# Conditional FRPs

Conditional FRPs are essentially functions that take a possible
input value and return an FRP corresponding to that input. A
Conditional FRP represents the output of a later stage of a random
process given the output of the earlier stages.

A conditional FRP is used primarily with join operations to build
larger systems from simpler pieces. We separate the system's output
into one or more stages, an initial FRP and a series of conditional
FRPs. Joining these successively gives the output of the system at
successive stages because a join preserves the entire history.

We construct conditional FRPs with the `conditional_frp` function in
a variety of ways, described in *Constructing Conditional FRPs*.

We can also evaluate, transform, join, and take the expectation of a
conditional FRP, as described in subsidiary topics.
