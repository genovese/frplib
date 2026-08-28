# mutual_information

Returns the mutual information I(Y; X) where Y and X are derived from a join.

This is called with `mutual_information(kX, cZ)`, where `kX`
is either a Kind or FRP and `cZ` is either a conditional Kind or
a conditional FRP compatible with `kX`. (Note: if `kX` is an FRP,
then `cZ` should be a conditional FRP and vice versa.)

We get `kY` from the join `kX >> cZ` followed by projection.
For a Kind/FRP `kX` and a conditional Kind/FRP `cZ`, `kY` is defined by
by
```
      kY = cZ // kX
```
The function computes and returns `I(kY; kX) = H(kY) - H(kY | kX)`.
