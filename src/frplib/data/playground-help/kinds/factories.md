# Custom Kind Factories

An **Kind factory** is a function that returns a Kind.
Typically, the parameters of the function give a specification
of the Kind's properties.

`frplib` offers the decorator `@kind_factory` that can be attached
to such a function. This has two benefits:

+ It clearly marks the intent of the function.

+ It makes the factory self-documenting in the playground. 

When the factory itself is printed, it displays a short docstring
rather than an opaque Python representation.

The factory can return either a Kind or a Kind. The latter will
automatically be converted to a fresh Kind with that Kind.

The docstring for that function should assume that the first
line will be preceded by "A factory producing a Kind that represents "
and should be written accordingly. The first line should *not* end
in a period.

The docstring for the factory will be built from the docstring
for the function, but can also be set with the `doc=` parameter
to the decorator. The primary use case for this is when you
want that docstring to include something dynamic from the calling
environment. If your docstring has rich markup that you
want displayed, set `allow_markup=True` in the decorator.

Examples:

```python
from frplib.exceptions import FactoryError

@kind_factory
def uniform_count(n):
    """a count in 1..n, equally weighted"""
    if not isinstance(n, int) or n < 0:
        raise FactoryError(f'UniformCount expects a natural number, received {n}')
    return uniform(0, 1, ..., n)
    
@kind_factory
def choices(n):
    """n independent binary choices"""
    if not isinstance(n, int) or n < 0:
        raise FactoryError(f'UniformCount expects a natural number, received {n}')
    return binary() ** n

@kind_factory(allow_markup=True)
def traffic_light(start):
    """the state of a traffic light: 0 [red]red[/red], 1 [yellow]yellow[/yellow], 2 [green]green[/green]"""
    return uniform(0, 1, 2) ^ ((__ + 1) % 2)
```
