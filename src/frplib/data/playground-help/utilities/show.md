# show

```
show(object)
```

Displays Python objects (lists, sets, tuples, dicts) that contain
frplib quantities in a more friendly way. This recurses through
such objects and produces prettier output.

A good example is if you have a list of symbols. Looking at that
list shows their python representation as objects, but calling `show`
on that list will print the symbolic strings. Similarly for FRPs
and so forth.

Currently, the indentation for kinds within lists is a bit off,
but that will be fixed.
