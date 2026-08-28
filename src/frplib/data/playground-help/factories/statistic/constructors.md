# Constructing Custom Statistics

There are three smart constructors for building statistics
out of functions:

+ `statistic` - convert a general function into a statistic
+ `scalar_statistic` - convert a function returning a scalar into a statistic of dimension 1
+ `condition` - convert a Boolean function into a special type of statistic, a condition

Each of these can be used as functions or as decorators on function definitions.

For example,
```
    @statistic
    def double(x):
        return 2 * x

    @condition
    def have_odd_difference(a, b):
        return (b - a) % 2 == 1

```
are equivalent to
```
    def double(x):
        return 2 * x

    def have_odd_difference(a, b):
        return (b - a) % 2 == 1

    double = statistic(double)
    have_odd_difference = condition(have_odd_difference)
```
Note that both of these can be more concisely defined
with Statistic expressions:
```
    (2 * __)
    ((Proj[2] - Proj[1]) % 2 == 1)
```
which you choose is a matter of preference in such cases.
For sufficiently complicated statistics, a custom statistic
is often the cleanest choice.

Moreover,
all three functions take a variety of arguments that can configure properties
of the returned statistics in useful ways..
The full signatures are
```
statistic(fn, name, codim, dim, description, monoidal, arg_convert, strict)
scalar_statistic(fn, name, codim, description, monoidal, arg_convert, strict)
condition(fn, name, codim, description, strict)

```
All arguments other than the function (`fn`) are optional.
`scalar_statistic` is identical to `statistic` except that enforces `dim=1`.
`condition` always has dimension 1 and does not do support either a
monoidal unit or argument conversion.

+ `name` - a string that will be used to name the statistic examining it in the playground

+ `codim` - sets the codimension (arity) of the statistic; the dimension of tuples
   it accepts. It can be either None (any codimension), a natural number (0..), or a pair (lo, hi)
   where lo <= hi, lo is a natural number, and hi is either a natural number or `infinity`.
   The latter indicates that the codimension is from lo..hi.

+ `dim` - the dimension of the tuple the statistic returns. This is `None` if it cannot
  be restricted, or a natural number. Statistics that return different dimension
  outputs for different dimension inputs should have `None` for this (the default)

+ `description` - a one line documentation string that is part of the description
  of the statistic in the playground. It should be a phrase that makes sense
  after "a statistic that returns...".

+ `monoidal` - if this is a monoidal statistic, this should be the monoidal unit

+ `arg_convert` - if supplied, this should be a function that can accept each
  component of the input tuple. The input is converted to a new tuple whose
  components are the output of this function on the original input components.

***NOTE**: If `codim` is 1 or (1, 1), then the argument is passed to the 
statistic ***as is***. In particular, it is not wrapped in a vector-tuple
as it usually is with statistics. This is to make it easy to define
scalar functions without lots of explicit wrapping and unwrapping.
You can use `arg_convert` if you need the input to be a particular
form, e.g., `float` or `as_quantity`.

See *Statistics::Defining Custom Statistics* info topic for more detail
on defining custom statistics, which uses these constructors.
