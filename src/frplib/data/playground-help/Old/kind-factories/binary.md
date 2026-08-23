# binary

`binary(p='1/2')` is a Kind representing a binary choice between 0
and 1 with respective weights `1-p` and `p`. By default, `p` is 1/2,
making `binary()` a synonym for `either(0, 1)`.

The weight `p` can be any quantity but if numeric should satisfy `0 <= p <= 1`.

