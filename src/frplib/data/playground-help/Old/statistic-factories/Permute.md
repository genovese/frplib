# Permute

Permute is a statistic factory that produces permutation statistics.
The permutations can be specified either by giving the cycle
decomposition (the default because it is usually easier) or the
direct mapping that indicates where each item maps to.

`Permute` accepts a list of (1-indexed) component indices (either as
individual arguments or as a single iterable). 

If cycle=True (the default), the indices are interpreted as a cycle
specification, where each cycle is listed in a specific way: with
its **largest element first** and cycles are listed in 
**increasing order of their largest element**.

For example, `Permute(4, 2, 7, 3, 1, 5, cycle=True)` maps `<1, 2, ..., 8>` 
to `<3, 4, 7, 2, 1, 6, 5, 8>`, with cycles (42) and (7315).

Similarly, `Permute(3, 1, 2)` takes the third element to position
one, the first to position two, and the second to position three.

If cycle=False, the indices should contain all values 1..n exactly
once for some positive integer n. Each index indicates which value
of the input vector goes in that position.

For example, `Permute(4, 2, 7, 3, 1, 5, 6, cycle=False)` maps `<1, 2, ..., 8>`
to `<4, 2, 7, 3, 1, 5, 6, 8>`.

Similarly, `Permute(3, 2, 1)` means that the original 3rd component is
first and the original 1st component is third. Similarly, `Permute(3, 1, 2)`
rearranges in the order third, first, second.

In either case, if m is the maximum index given, then the
permutation has codimension k for every k >= m. Values above the
maximum index are left in their original place.

More Examples:
+ `Permute(3, 1, 4, 2)` takes `<a, b, c, d>` to `<c, d, a, b>`
+ `Permute(4, 1, 2, 3, cycle=False)` takes `<a, b, c, d>` to `<d, a, b, c>`
