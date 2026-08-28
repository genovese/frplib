# Round

`Round` is a factory returning a statistic that rounds a number to a
specified number of digits

The signature is `Round(digits)` where `digits` is an integer.

If `digits` is positive, the returned statistic rounds numeric
quantities to that many places after the decimal point. If `digits`
is negative, the statistic rounds to the nearest `-digits` power of
10.

Symbolic quantities are passed through the statistic as is.

Examples

+ `tup(1, 99.2343456, 256.652, 12345.678) ^ ForEach(Round(2))` => `<1, 99.23, 256.65, 12345.68>`
+ `tup(1, 1.2343456, 2.5, 2.11111111111) ^ ForEach(Round(4))` => `<1, 1.2343, 2.5000, 2.1111>`
+ `tup(1, 1.2343456, 2.5, 2.11111111111) ^ ForEach(Round(0))` => `<1, 1, 3, 2>` 
+ `tup(1, 99.2343456, 256.652, 12345.678) ^ ForEach(Round(-1))` => `<1.0, 99.0, 257.0, 12346.0>`
+ `tup(1, 99.2343456, 256.652, 12345.678) ^ ForEach(Round(-2))` => `<0.0, 100.0, 260.0, 12350.0>`
+ `tup(1, 99.2343456, 256.652, 12345.678) ^ ForEach(Round(-4))` => `<0.0, 0.0, 0.0, 12000.0>`
