# given

`given` is used in FRP and Kind procedures to update with an
obervation. In a procedure, we use
```
    yield given(obs)
```
to enforce the condition that observation `obs` is true.
Here, `obs` can be an actual Boolean (True or False) or
an `frplib` Boolean tuple (<1> or <0>, or the numbers 1 or 0).
It is always used with `yield` and the yielde value is ignored.

For example, if `k` is a Kind
```
    @kind
    def updated_k():
        x = yield k
        yield given(x > 10)
        return x
```
This is the Kind expressed in operator as `k | (__ > 10)`.

The procedure form comes into its own with complex combinations
of operations
```
    @kind
    def updated_k():
        x = yield k
        yield given(x > 10)
        y = yield r
        return join(x, y) ^ psi
```
equals `psi( (k | (__ > 10)) * r )` which is notably less clear.
