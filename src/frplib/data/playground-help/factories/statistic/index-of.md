# IndexOf

The statistic factory `IndexOf` produces a statistic that returns
the first index of the specified tuple within its input tuple, or -1
if none.

Accepts a single sequence or multiple arguments that are combined into a sequence.

Parameter `items` is an indexable sequence. This tests if this sequence
is a contiguous subsequence in the input tuple, returning the (0-based) index
of the *first* occurrence, or -1 if no subsequence is found.

See Contains() for an analogous condition.

Examples:
+ `tup(0, 1, 2, 3, 4, 5, 6) ^ IndexOf(4, 5)` => 4
+ `tup(0, 1, 2, 3, 4, 5, 6) ^ IndexOf(4, 7)` => -1
+ `tup(0, 1, 2, 3, 4, 5, 6) ^ IndexOf(2)`    => 2
+ `tup(0, 1, 2, 3, 4, 5, 6) ^ IndexOf(9)`    => -1
