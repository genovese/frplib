# Cases

The statistic factory `Cases` represents a dictionary and optional default.
When the statistic is given a value that is a key in the dictionary,
the dictionary value is returned. Otherwise, the default value is returned.

The dictionary specifies the mapping from inputs to outputs. The
statistic may have multiple codimensions, but all all outputs with
the same input dimension must share a common dimension. If all
inputs have the same dimension and default is supplied with the same
dimension as well, then the statistic will return the default value
for any input that is not a key of the dictionary. Scalars are
auto-converted and can be used for keys, values, and default.

Examples:
+ `Cases({1: 0, 10: 1, 100: 2, 1000: 3}, default=-1)` will return 0, 1, 2, or 3
    for respective inputs 1, 10, 100, or 1000.  Any other input will return -1.

+ `Cases({1: 0, 10: 1, 100: 2, 1000: 3})` will return 0, 1, 2, or 3
    for respective inputs 1, 10, 100, or 1000.  Any other input will raise an error.

Returns a statistic with properly recorded type.

Added in v0.2.4.
