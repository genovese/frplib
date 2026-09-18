# The Factory Trick

A ZZZ factory is a function that returns a ZZZ made to a
specification determined by the functions arguments.
`frplib` uses factories in many places:

+ FRP Factories
+ Kind Factories
+ Statistic Factories
+ Condition Factories

along with custom factories that you yourself can write.

We create a ZZZ factory by writing a functio that returns a ZZZ. If
we mark it with one of the builtin decorators (`@frp_factory`,
`@kind_factory`, `@statistic_factory`, or `@condition_factory`),
then the factory object will print nicely in the playground, taking
its documentation from the objects docstring (where appropriate).

See info documents *Kinds::Custom Kind Factories*,
*FRPs::Custom FRP Factories*, and *Statistics::Custom Statistic and Condition
Factories* for examples and more detail. This is also illustrated in
the textbook.

But beyond these built-in cases, you can write a factory that
produces any type of object you like. The parameters of the factory
function specify the object created. The big advantage of this
trick is that the code producing the object has the parameters
of the factory in scope. And if the object is a function, it
will remember the values of those parameters thereafter.

As an example, consider a factory to describe an "evolvable system".
We need the Kind or FRP of the initial state and the conditional Kind or FRP
describing the state transition. 
```python

   def my_system(start: int, jump_size: int) -> tuple[Kind, ConditionalKind]:
       initial = constant(start)

       @conditional_kind(codim=1, target_dim=1)
       def transition(state):
           return uniform(-jump_size, 0, jump_size) ^ (__ + state)

       return (initial, transition)
```
This takes two integers that specify the system and return
both the Kind of the initial state and the conditional Kind
describing the transition. The key thing is that the transition
will remember the value of `jump_size`. So we can call `my_system`
many different times, with different parameters, and get perfectly
viable, distinct systems as a result.
