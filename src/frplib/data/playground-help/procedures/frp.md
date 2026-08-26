# FRP Procedures

Procedures provide a clear and compact way to create FRPs that
combine many different operations. As an alternative to operator
style, procedures provide a different perspective that does
not get unduly complicated when it involves many operations.

The `@frp` decorator on a function signals a Kind procedure.
```python
    @frp
    def k():
        x = yield uniform(1, 2, 3)
        y = yield uniform(-1, 0, 1, 10)
        return x + y
```

***ATTN:MORE TO COME***
