# average_conditional_entropy

Returns the average (predicted) conditional entropy of the join kX >> cZ.

This is called with `average_conditional_entropy(kX, cZ)`, where `kX`
is either a Kind or FRP and `cZ` is either a conditional Kind or
a conditional FRP compatible with `kX`. (Note: if `kX` is an FRP,
then `cZ` should be a conditional FRP and vice versa.)

If `kX` represents an FRP `X` and `kY = cZ // kX` represents an FRP
`Y`, then in mathematical notation this returns the average
conditional entropy H(Y | X).
(For reference, `cZ.conditional_entropy(x)` gives H(Y | X = x).)
