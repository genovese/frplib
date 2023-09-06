# irange

Creates *i*nclusive *i*nteger ranges; like Python's `range` but
includes the endpoint and generates only integers.

The signature is
```
irange(start_or_stop, stop=None, *, step=1, exclude=None, include=None)
```

Inclusive integer range.

## Parameters

+ `start_or_stop` - if the only argument, an integer giving the stop (inclusive)
      of the sequence; if stop is also supplied, this is the start.
+ `stop` - if missing, start from 1 (unlike the builtin range that starts from 0);
      otherwise, the sequence goes up to and including this value.
+ `step` - a non-zero integer giving the spacing between successive values of the
      sequence; it can e negativ if stop < start.
+ `exclude` - either a set of integers or a predicate taking integers to boolean
      values; values in the set or for which the predicate returns true are skippe.
+ `include` - either a set of integers or a predicate taking integers to boolean
      values; values in the set or for which the predicate returns true are included.
      If exclude is also supplied, this takes precedence.

## Returns

An iterator over the resulting range.

## Examples

+ `irange(52)` :: integers from 1 to 52
+ `irange(52, exclude=lambda i: i % 2 == 0)` :: odd integers from 1 to 52
+ `irange(52, exclude={4, 7, 17})` :: integers from 1 to 52 except for 4, 7, 17
