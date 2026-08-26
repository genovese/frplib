# Freqs

The statistic `Freqs` returns the counts of unique components in the
input tuple in descending order

The dimension of the output tuple is always equal to the dimension
of the input tuple. Unneeded components are padded with the special
`nothing` value, which always comes at the end.

It expects a tuple of positive dimension.

Examples: 

+ `Freqs(2, 3, 2, 2, 4, 3)` == <3, 2, 1, _, _, _>
+ `Freqs(1, 1, 1, 1, 1, 7)` == <5, 1, _, _, _, _>
+ `Freqs(1, 2, 3, 4, 5, 6)` == <1, 1, 1, 1, 1, 1>
+ `Freqs(2, 2, 4, 6, 8, 0)` == <2, 1, 1, 1, 1, _>
