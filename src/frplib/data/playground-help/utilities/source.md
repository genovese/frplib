# source

`source` is a utility for use within the frplib playground. For a
defined function or callable object `fn`, `source(fn)` displays the
function source code, if it can be located.

This works for plain functions, and for frplib's wrapped objects,
which includes factories (uniform, constant, shuffle, etc.),
conditional Kinds/FRPs built from a function, and Statistics.

Note: A conditional Kind/FRP built from a dict has no separate
source to show, and this reports that cleanly.

Some callable objects are defined by a function in an internal scope,
which may be displayed by `source`. But `source` attempts to find
the correct frame when possible.
