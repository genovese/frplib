The frplib **playground** is an enhanced Python REPL (Read-Evaluate-Print-Loop)
that is preloaded with the frplib resources and that provides nice interactive
output and help for frplib functions, objects, and data.

For example, here we create a kind, an FRP from that kind, and display both:

```
  playground> k = uniform(1, 2, ..., 10)
  playground> k
    # ...displays a picture of the kind
  playground> X = frp(k)
  playground> X
    # ...displays the FRP's value
```

The prompt for entry is `playground>`, and when input extends over
multiple lines, it will show the continuation prompt `...>` to
indicate this. You need to hit an extra newline to end multiline
input.

You can get help using the `info()` function and the builtin Python
`help()`. Enter `info()` to get started and see a list of available
topics. You can also apply `info()` to objects in the playground,
and it will attempt to show the appropriate topic if possible (or
help if not). For example, `info(uniform)` finds the topic associate
with the uniform factory. Use `help()` to get more detailed usage
documentation on functions from both frplib and Python.
