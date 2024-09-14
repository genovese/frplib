# weighted_pairs

`weighted_pairs(*pairs)` returns a Kind specified by a sequence of `(value, weight)` pairs.

Pairs can be given as a single iterable argument, like a list or a generator,
or can be given as multiple tuple arguments, one per pair.

Values will be converted to quantitative vectors and weights
to quantities. both can contain numbers, symbols, or strings.
Repeated values will have their weights combined.

Examples: 
+ `weighted_pairs((1, '1/2'), (2, '1/3'), (3, '1/6'))`
+ `weighted_pairs([(1, '1/2'), (2, '1/3'), (3, '1/6')])`
+ `weighted_pairs(((x, y), x + y) for x in irange(1, 3) for y in irange(1, 3))`
