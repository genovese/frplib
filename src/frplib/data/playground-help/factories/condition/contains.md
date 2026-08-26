# Contains

The condition factory `Contains` returns a condition that tests if a
specified tuple is within its input tuple, or -1 if none.

Accepts a single sequence or multiple arguments that are combined into a sequence.

Parameter `items` is an indexable sequence. This tests if this sequence
is a contiguous subsequence of the input tuple, returning true (1) if so
or false (0) otherwise.

See IndexOf() for an analogous statistic that finds the first index.

Examples:
+ `tup(0, 1, 2, 3, 4, 5, 6) ^ Contains(4, 5)`  => 1
+ `tup(0, 1, 2, 3, 4, 5, 6) ^ Contains(4, 7)`  => 0
+ `tup(0, 1, 2, 3, 4, 5, 6) ^ Contains(2)   `  => 1
+ `tup(0, 1, 2, 3, 4, 5, 6) ^ Contains(9)   `  => 0
