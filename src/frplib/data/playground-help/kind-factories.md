# Kind Factories

Kind factories are, as the name suggests, functions that produce kinds.
We use them in practice as building blocks for kinds that have certain
patterns of weights on specified values.

## General Factories

+ `kind` :: a generic constructor that produces kinds from a variety of inputs.
+ `conditional_kind` :: create conditional kinds from functions or dictionaries
+ `lazy` :: optimizes kind computation for large sizes (not currently available)

## Factories for Patterns of Weights on Given Values

+ `constant` :: the kind of a constant FRP with specified value
+ `uniform` :: a kind with specified values and equal weights
+ `either` :: a kind with two possible values and with a specified weight ratio
+ `weighted_as` :: a kind with the specified values weighted by given weights
+ `weighted_by` :: a kind with the specified values weighted by a function of those values
+ `weighted_pairs` :: a kind specified by a sequence of (value, weight) pairs
+ `symmetric` :: a kind with weights on values determined by a symmetric function around a specified value
+ `linear` :: a kind with the specified values and weights varying linearly
+ `geometric` :: a kind with the specified values and weights varying geometrically
+ `arbitrary` :: a kind with the given values and arbitrary symbolic weights

## Specialized Factories
+ `integers` :: kind of an FRP whose values consist of integers in a regular sequence
+ `evenly_spaced` :: kind of an FRP whose values consist of evenly spaced numbers
+ `without_replacement` :: kind of an FRP that samples n items from a set without replacement
+ `subsets` :: kind of an FRP whose values are subsets of a given collection
+ `permutations_of` :: kind of an FRP whose values are permutations of a given collection
+ `ordered_samples` :: like `without_replacement` but gives ordered samples (all permutations)

## Available Sub-topics

+ `kind`, `constant`, `uniform`, `either`, `weighted_as`
