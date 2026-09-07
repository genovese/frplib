# Construction of Conditional Kinds

The `conditional_kind` function is used to construct Conditional
Kinds in a variety of ways.

+ Passing a dictionary whose keys are values (or numbers in the codim 1 case)
  and whose "values" are Kinds.
  
+ Passing a function that accepts values and returns Kinds.

+ Used as a decorator on a function definition.

In this latter case, the argument specification in the function
definition can be used to deconstruct the input tuple.

For example:

```python
    @conditional_kind
    def ck(x):
        ...
```
In this case, the input is a tuple of arbitrary dimension.
Its dimension can be constrained with the codim argument.
```python
    @conditional_kind(codim=6)
    def ck(x):
        ...
```
This requires that `x` has dimension 6. It can be set as well
to a tuple (a, b) meaning any value from a through b (inclusive).

The one special case is codim=1. In this case, the argument to
the function is passed as is, with no tuple conversion. This
is intended to make it easy to pass floats to functions that
desire them.

Multiple arguments can be supplied which will both set
the codimension and will destructure the tuple into the
named arguments.

```@python
    @conditional_kind
    def ck(a, b, c):
        ...

    @conditional_kind
    def ck(a, b, c, *d):
        ...
```
The first case will give codimension 3 and those compoents are
accessible through the *quantities* `a`, `b`, and `c`.
In the second case, the codimension will be (3, infinity)
and `d` will hold all the components after the first three
in the input tuple.

Note: In code within a python program, type checkers like mypy can
have trouble with the type if passed a variable holding a dictionary
for the input. The flexible type signature of `conditional_kind`
raises difficulties there. Passing a literal dictionary eliminates
such problems, as does a `# type: ignore` comment.
