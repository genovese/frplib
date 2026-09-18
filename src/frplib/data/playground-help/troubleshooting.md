# Troubleshooting

The `frplib` playground allows you to run arbitrary Python code, but it
treats operations of `frplib` objects specially. When errors are
detected in your code, the playground attempts to display a helpful
and meaningful error message.

Sometimes the error message is not enough to track down the problem.
The function `explain_error()`, called just after an operation that
raises an error, will show you more information, including the full
exception stack. Errors like `KeyError` and `IndexError` are handled
specially in the playground to help you locate the problem, with
and without `explain_error()`. But this is useful for any errors.

Besides simple typing errors, the most common errors arise from
mismatches in what type of object an operation expects and what is
given. So this is a good thing to check when you encounter problems.

In more extreme cases, you can insert a call to `breakpoint()` in
your code, and when this is called, it will enter the Python debugger.
Lookup documentation on the `pdb` Python library for details
about using the debugger, but here's a simple example.

```python
    @condition
    def foo(xs):
        for x in xs:
            breakpoint()
            if x == 10:
                return True
        return False
```

Now when you call `foo(1, 2, 3, 10)`
you will enter the debugger and can look
at the environment (e.g., `x`)
```
playground> foo(1, 2, 3, 10)
> <playground-1>(4)foo()
-> breakpoint()
(Pdb) p x
1
(Pdb) c
> <playground-1>(4)foo()
-> breakpoint()
(Pdb) p x
2
(Pdb) c
> <playground-1>(4)foo()
-> breakpoint()
(Pdb) p x
3
(Pdb) c
> <playground-1>(4)foo()
-> breakpoint()
(Pdb) p x
10
(Pdb) c
<1>

playground>
```
