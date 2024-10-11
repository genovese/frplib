# Kind Factories

Kind factories are, as the name suggests, functions that produce Kinds.
We use them in practice as building blocks for Kinds that have certain
patterns of weights on specified values.

## General Factories

+ `kind` :: a generic constructor that produces Kinds from a variety of inputs.
+ `conditional_kind` :: create conditional Kinds from functions or dictionaries

## Factories for Patterns of Weights on Given Values

+ `constant` :: the Kind of a constant FRP with specified value
+ `binary` :: a Kind that has values 0 and 1 with specified weight on 1
+ `either` :: a Kind with two possible values and with a specified weight ratio
+ `uniform` :: a Kind with specified values and equal weights
+ `weighted_as` :: a Kind with the specified values weighted by given weights
+ `weighted_by` :: a Kind with the specified values weighted by a function of those values
+ `weighted_pairs` :: a Kind specified by a sequence of (value, weight) pairs
+ `symmetric` :: a Kind with weights on values determined by a symmetric function around a specified value
+ `linear` :: a Kind with the specified values and weights varying linearly
+ `geometric` :: a Kind with the specified values and weights varying geometrically
+ `arbitrary` :: a Kind with the given values and arbitrary symbolic weights

## Specialized Factories
+ `integers` :: Kind of an FRP whose values consist of integers in a regular sequence
+ `evenly_spaced` :: Kind of an FRP whose values consist of evenly spaced numbers
+ `without_replacement` :: Kind of an FRP that samples n items from a set without replacement
+ `ordered_samples` :: Kind of an FRP representing all ordered samples of size n from
                       a given collection of values
+ `subsets` :: Kind of an FRP whose values are subsets of a given collection
+ `permutations_of` :: Kind of an FRP whose values are permutations of a given collection
+ `ordered_samples` :: like `without_replacement` but gives ordered samples (all permutations)

## Available Sub-topics

+ `kind`, `constant`, `uniform`, `either`, `weighted_as`, `evenly_spaced`, `without_replacement`,
  `binary`, `weighted_pairs`, `weighted_by`
