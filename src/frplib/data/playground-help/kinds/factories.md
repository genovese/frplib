# Custom Kind Factories

A **Kind factory** is a function that returns a fresh Kind.
Typically, the parameters of the function give a specification
of the Kind's properties.

`frplib` offers the decorator `@kind_factory` that can be attached
to such a function. This has two benefits:

+ It clearly marks the intent of the function.

+ It makes the factory self-documenting in the playground. 

When the factory itself is printed, it displays a short docstring
rather than an opaque Python representation.

The docstring for that function should assume that the first
line will be preceded by "A factory producing a Kind that represents "
and should be written accordingly.

***ATTN: More to Come***
