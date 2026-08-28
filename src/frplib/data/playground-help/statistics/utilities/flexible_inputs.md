# flexible_inputs

`flexible_inputs` is a decorator that can be applied to a
tuple-accepting function so that it accepts either multiple
individual arguments as the tuple components or a single tuple.

Example:
```
@flexible_inputs
def swap(x):
    a, b = x
    return (b, a)
    
swap(1, 2)    #=> (2, 1)
x = (4, 2)
swap(x)       #=> (2, 4)
swap((4, 2))  #=> (2, 4)
```
