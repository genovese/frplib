# FRP Factories

FRP factories are, as the name suggests, functions that produce FRPs.

The main factory is `frp` which takes a kind (or another FRP with a kind)
and creates a new FRP with that kind (or a clone of a given FRP).

In addition, `conditional_frp` is used to construct conditional FRPs.
This takes either a dictionary mapping values to FRPs or a function
mapping values to FRPs.  All values should be of the same dimension
and should be FRPs (with or without computed kinds).

The specialized factory `shuffle` takes an iterable containing some values
and returns an FRP whose values are shuffles, or permutations of those
values. This is fairly efficient and so can be used to generate random
permutations of even moderately large lists of items.
