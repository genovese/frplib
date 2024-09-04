# frplib Modules

The following modules can be imported and used within your code to
access `frplib` functionality. You can also selectively import
objects from any of these modules; see the topic `object-index` for
the module containing commonly used `frplib` functions and objects.

Importing an object from one of these modules looks like one of the 
following

```
    from MODULE import NAME
    from MODULE import NAME1, NAME2, NAME3, ...
    from MODULE import *
```

where `MODULE` is replaced the name of a module below and `NAME`
(and `NAME1`, `NAME2`, `NAME3`, `...`) are replaced with the names
of the objects to load. Using `*` imports all available objects
from that module.

Alternatively, you can import the module with

```
    import MODULE as MNAME
```

and use `MNAME.NAME` to refer to objects in that module.


The playground loads most of these modules
automatically and many functions and objects
from them, but you can use these import statements
in the playground as well.

The principle `frplib` modules are:

+ `frplib.calculate` :: tools for specialized calculation, currently
    mostly substitution of symbolic terms
+ `frplib.exceptions` :: specialized `frplib` exception types
+ `frplib.expectations` :: operators like `E` and `D_` and `Var`
    for computing expectations and related functions.
+ `frplib.extras` :: additional high-level utilities
+ `frplib.frps` :: FRP factories and combinators
+ `frplib.kinds` :: Kind factories and combinators
+ `frplib.numeric` :: functions for numeric conversions and computations.
+ `frplib.quantity` :: functions for creating the high-precision
    decimal quantities `frplib` uses for most calculations.
+ `frplib.statistics` :: a wide variety of built-in statistics,
    statistic factories, and statistic combinators.
+ `frplib.symbolic` :: tools for building symbolic quantities.
    These represent expressions on variables that do not (yet)
    have a numeric value.
+ `frplib.utils` :: a variety of useful functions for operating
    on FRPs, Kinds, tuples, sequences, collections, and functions.
    See `info("utilities")` for highlights.
+ `frplib.vec_tuples` :: functions for building and manipulating
    the specialized "vector" tuples used by `frplib`
+ `frplib.examples.*` :: separate modules for most named examples
    in the text, e.g., `frplib.examples.monty_hall`. Most are
    named with up to the first three words of the example title
    with spaces separated by underscores.
