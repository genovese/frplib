# Builtin Statistic Factories

+ `Proj` :: A factory that creates projection statistics over specified indices.
+ `Constantly` :: A factory producing a statistic that always returns the specified value.
+ `Permute` :: A factory producing a statistic that produces permutation statistics.
+ `Append` :: A factory producing a statistic that appends specified values to its input.
+ `Prepend` :: A factory producing a statistic that prepends specified values to its input.
+ `Cases` :: A factory producing a statistic that represents a dictionary and optional default.
+ `Get` :: A factory producing a statistic that accesses a python object with [] with the input as index.
+ `IndexOf` :: A factory producing a statistic that returns the first index of the specified tuple within its input tuple, or -1 if none.
+ `Keep` :: A factory producing a statistic that keeps components of its input that satisfy a specified predicate.
+ `MaybeMap` :: A factory producing a statistic that applies a statistic to every input component, keeping those whose value is not
nothing/None.
+ `Round` :: A factory producing a statistic that rounds a number to a specified number of digits.
+ `Dot` :: A factory producing a statistic that returns the vector dot product with a specified vector tuple.
+ `ChiSquare` :: A factory producing a statistic that computes the Chi-square statistic on the input against the specified expected
components.
