# is_quantifable

`is_quantifiable` tests whether the given value is convertible to a `quantity`.

This is true for any value for which as_quantity returns a valid quantity.
This includes various numeric types (int, float, Fraction, Decimal, NumericQuantity)
as well as Symbolic values and Nothing.
