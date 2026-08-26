# ForEach

+ `ForEach` :: apply a given statistic to every component of a value,
    so  `ForEach(s)` maps `<v1, v2, ..., vn>` to `<s(v1), s(v2), ..., s(vn)>`,
    where the results of the statistics are concatenated into
    a single tuple.
    If `s` is a constant, it is automatically wrapped in `Constantly`.

The `ForEach` combinator takes a statistic
and creates a new statistic that applies the given statistic
to every component of the input tuple.

`ForEach(s)` maps `<v1, v2, ..., vn>` to `<s(v1), s(v2), ..., s(vn)>`,
where the results of the statistics are concatenated into a single
tuple. If `s` is a constant, it is automatically wrapped in
`Constantly`.

Examples

+ `tup(-10, 20, -3) ^ ForEach(Abs)` => <10, 20, 3>
+ `tup(-1, 0, 2, 10) ^ ForEach(__ ** 2)` => <1, 0, 4, 100>
+ `tup() ^ ForEach(s)` => <>
