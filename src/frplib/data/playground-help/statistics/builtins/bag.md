# Bag

Statistic `Bag` returns a bag computed from input, encoded as
alternating values and counts, with values in ascending order. It
accepts a tuple of any dimension.

The returned tuple is of the form `<v_1 c_1 v_2 c_2 ...>`
where the `v_i`'s are the unique values in the input tuple in ascending order
and `c_i` is the number of times `v_i` appears in the tuple.

Examples

+ `Bag(1, 1, 1, 1)` => <1, 4>
+ `Bag(1, 1, 1, 1, 1)` => <1, 5>
+ `Bag(1, 2, 1, 2, 1, 2, 1, 3, 3)` => <1, 4, 2, 3, 3, 2>
+ `Bag()` => <>
