# Projections

Projections are statistics that extract one or more components
from the tuple passed as input.

In frplib, `Proj` is a factory for creating projection statistics.
We specify which projection is produced by indicating the
components in brackets, like indexing an array. The components
for a projection statistic are **1-based**, so the first component
has index 1 (not 0 like in Python).

So for example, `Proj[1]` is the projection that returns the
first component of a tuple and `Proj[1, 3, 5]` returns a new
tuple with the first, third, and fifth components of its argument.

The `Proj` factory supports a variety of ways to select components.
The following forms can be used within the `[]` brackets:

  + a single, positive integer `i` selects the ith component
  + a single, negative integer `-i` selects the ith component
    *from the end*, with -1 being the last componet, -2 the
    second to last, and so forth.
  + a list of non-zero integers selects the corresponding
    components in order and puts them in a new tuple.
    Both positive and negative indices can be used, and indices
    can be repeated.
  + a slice of the form `i:j` selects all components from `i`
    up to but not including `j`. This works with both positive
    and negative indices, so `Proj[2:-1]` extracts all but
    the first and last components.
  + a slice with one side missing, either `i:` or `:j`.
    The former selects from `i` to the end; the latter
    from the beginning up to but not including `j`.
  + a slice with skip `i:j:k` selects from `i` up to 
    but not including `j`, skipping by `k` components
    at each step.

The `Projbar` factory is like `Proj` but the specification
in brackets indicates which components to *exclude*.

See Chapter 0, Section 2.3 for more detail.
