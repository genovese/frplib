# Defining Custom Statistics

We can define custom statistics by binding statistic expressions to variables
```python
   first_and_last = Proj[1, -1]
```
or by defining decorated functions
```python
   @statistic(dim=2)
   def first_and_last(x):
       return (x[0], x[-1])
```
As the former is straightforward, we focus here on the latter.

The decorators

+ `@statistic` for a general statistic,
+ `@scalar_statistic` as a short-hand for a statistic of dimension 1, and
+ `@condition` for a condition

are put before a function definition to turn that function
into an `frplib` Statistic or Condition object. The resulting Statistic or Condition
can be called like a function and used in statistic expressions and provides
other capabilities like queries and documentation strings.

These decorators can be used with no arguments (and no parentheses!).
For example:
```python
   @statistic
   def even_elements(x):
       return x[0::2]
```
However, the decorators take a variety of arguments to specify
properties of the resulting statistic:

+ `codim` :: Either a natural number, a pair (a, b) natural numbers
   (though b can also be `infinity`) giving the range of valid input
   dimensions (from a to b), or `None`, meaning that any input
   dimension is valid. The `codim=1` case is handles specially, see
   below.
   
+ `dim` :: The dimension of the output tuple, either a natural number
   or `None`, meaning unknown.

+ `name` :: A string naming the statistic when printed.

+ `description` :: Help text for the statistic in help or info or when printed.

+ `monoidal` :: If supplied indicates this is a monoidal statistic and the
  value should be the unit (identity element) of the monoid.
  
+ `arg_convert` :: If supplied, a function applied to each component of
  the input tuple to convert it to some desired form.
  
The input and output of a statistic are automatically converted into
a vector tuple.

## Specifying arguments

If a statistic has a single positional argument, it will be assumed 
that that argument is a tuple unless codim=1 (see below).

With multiple arguments that is not the case, and the multiple
arguments are taken as the components. In this case, `frplib`
can infer the codimension; codim need not be supplied.
A `*arg` will be a tuple that represents the remaining components.
So with
```
   @statistic
   def foo(x, y, z):
      ...
      
   @condition
   def bar(first, second, *rest):
      ...

   @statistic
   def zap(x, y, z=99):
      ...
      

```
`foo` will have codimension 3; `bar` will have codimension `(2, infinity)`,
ad `zap` will have codimension `(2, 3)`.
When passed an input tuple, `foo` will unpack the three components into
`x`, `y`, and `z` automatically, and `bar` will unpack the first
two components into `first` and `second` and put the remaining components
into a standard tuple `rest`.
`zap` will do likewise, using the default value of `z` if the input
only has dimension 2.


## The codim=1 Case

When the codimension is set to 1 (technically 1 or (1, 1)), the input
the statistic is ***not*** wrapped in a tuple but passed in *as is*.
This is to make it convenient to write functions that accept scalars
by avoiding unpacking numbers. Note that Python floats are not generally
compatible with the high-precision quantities in `frplib` (though both
can be converted to the other). So be consistent in your usage
or pass `float` or `as_quantity` as `arg_convert` if needed.
