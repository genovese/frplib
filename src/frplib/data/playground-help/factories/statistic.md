# Builtin Statistic Factories

+ `Append` :: A factory producing a statistic that appends specified values to its input.
+ `Cases` :: A factory producing a statistic that represents a dictionary and optional default.
+ `ChiSquare` :: A factory producing a statistic that computes the Chi-square statistic on the input against the specified expected components.
+ `Constantly` :: A factory producing a statistic that always returns the specified value.
+ `Dot` :: A factory producing a statistic that returns the vector dot product with a specified vector tuple.
+ `Get` :: A factory producing a statistic that accesses a python object with [] with the input as index.
+ `IndexOf` :: A factory producing a statistic that returns the first index of the specified tuple within its input tuple, or -1 if none.
+ `Keep` :: A factory producing a statistic that keeps components of its input that satisfy a specified predicate.
+ `MaybeMap` :: A factory producing a statistic that applies a statistic to every input component, keeping those whose value is not nothing/None.
+ `Permute` :: A factory producing a statistic that produces permutation statistics.
+ `Prepend` :: A factory producing a statistic that prepends specified values to its input.
+ `Proj` :: A factory that creates projection statistics over specified indices.
+ `Round` :: A factory producing a statistic that rounds a number to a specified number of digits.
+ `Shift` :: A factory producing a statistic that shifts a tuples components with wraparound.
