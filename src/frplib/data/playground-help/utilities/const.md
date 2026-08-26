# const

`const(a)` returns a function that itself always returns the value `a`.
The value can be anything, and the returned function accepts exactly
one argument.

Example
```python
    f = const(10)
    f(4)     #=> 10
    f(0)     #=> 10
    f('foo') #=> 10
```
