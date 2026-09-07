# Conditional Kinds

Conditional Kinds are essentially functions that take a possible
input value and return a Kind corresponding to that input. A
Conditional Kind represents the output of a later stage of a random
process given the output of the earlier stages.

A conditional Kind is used primarily with join operations to build
larger systems from simpler pieces. We separate the system's output
into one or more stages, an initial Kind and a series of conditional
Kinds. Joining these successively gives the output of the system at
successive stages because a join preserves the entire history.

We construct conditional Kind with the `conditional_kind` function
in a variety of ways, described in *Constructing Conditional Kinds*.

We can also evaluate, transform, join, and take the expectation of a
conditional Kind, as described in subsidiary topics.

