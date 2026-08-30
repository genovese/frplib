# Custom Statistic Factories

An **Statistic factory** is a function that returns a statistic.
(Because a statistic is a type of function, this is a function
that returns a function.)
The parameters given to the factory specify the properties
of the Statistic.

`frplib` offers the decorators `@statistic_factory` and `@condition_factory`
that can be attached to such a function. These have two benefits:

+ They clearly mark the intent of the function.

+ They make the factory self-documenting in the playground. 

Use `@statistic_factory` for functions that return general statistics
and `@condition_factory` for functions that return the special
case of *conditions*.

When the factory itself is printed, it displays a short docstring
rather than an opaque Python representation.

A simple example of a statistic factory is
```python
    @statistic_factory
    def number_of(x):
        "counts the number of times a specified value appears in its input"

        @scalar_statistic
        def _number_of_x(v):
            cnt = 0
            for vi in v:
                if vi == x:
                    cnt += 1
            return cnt
            
        return _number_of_x
```
We define the statistic inside the factory. Here, we defined it as a decorated
function, but we can use a statistics expression or a constructor as we like.
Remember that we must *return* the statistic that we define.

In the example above, printing `number_of` at the playground prompt
will print "A factory producing a statistic that counts the number
of times a specified value appears in its input." The prefix "A
factory ... that" is added automatically by `frplib` so you don't
have to repeat the boilerplate. The first line should *not* end in a
period, and if your docstring has rich markup that you want
displayed, set `allow_markup=True` in the factory decorator.;

But printing the statistic `number_of(4)` prints a generic message.
We can change that by supplying a docstring to the `_number_of_x` function,
but such a string cannot depend on `x`. We can give it a name and a documentation
string with arguments to the inner decorator, like the following
```python
    @statistic_factory
    def number_of(x):
        "counts the number of times a specified value appears in its input"

        @scalar_statistic(name=f'Number_of({x})',
                          description=f'counts the number of times {x} appears in its input'
        def _number_of_x(v):
            cnt = 0
            for vi in v:
                if vi == x:
                    cnt += 1
            return cnt
            
        return _number_of_x
```
Now `number_of_x(4)` prints a meaningful message as well.

If you want to signal a factory-specific error, `frplib`
defines a `FactoryError` class that will print nicely
in the playground. For example:
```python
    @statistic_factory
    def components_at_multiples(n):
        "gives components of the input at indices that are multiples of a specified integer"
        if n <= 0:
            raise FactoryError('components_at_multiples requires a positive integer')
        return Proj[n::n]
```
Then for instance
```
playground> tup(1, 2, 3, 4, 5, 6, 7, 8, 9, 10) ^ components_at_multiples(3)
<3, 6, 9>
```
Similarly,
```python
    @component_factory
    def any_even_at_multiples(n):
        "tests if the input at indices that are multiples of a specified integer are even"
        if n <= 0:
            raise FactoryError('any_even_at_multiples requires a positive integer')
        
        return Proj[n::n] ^ Any(__ % 2 == 0)
```
Note how this uses the composition of statistics in an expression to
easily get the desired condition.
