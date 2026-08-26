# Dot

`Dot` is a statistic factory that represents the dot-product with a fixed vector.

For a tuple `v` of dimension `d`, `Dot(v)` is a statistic of co-dimension `d`
that maps `w` to
```
    v_1 * w_1 + v_2 * w_2 + ... + v_d * w_d
```

Examples

+ `tup(1, 1, 1) ^ Dot(1, -1, 0)` => <0>
+ `tup(1, 2, 3, 4) ^ Dot(1, 1, 1, 1)` => <10>
+ `tup(1, 0, 1, 0) ^ Dot(0, 1, 0, 1)` => <0>

