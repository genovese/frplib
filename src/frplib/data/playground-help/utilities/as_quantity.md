# as_quantity

Converts a quantifiable entity into an frplib quantity.

Quantifiables include numeric values (int, float, Fraction, Decimal, bool),
strings, symbols, and the special nothing item.
See `is_quantifiable`.

The full signature is
```
```
with parameters
 + `x`: the entity to be converted into a quantity
 + `convert_numeric`: the function used to do numeric conversion
    when `x` has a numeric type (default: `as_numeric`)
This raises an error if `x` is not quantifiable.
