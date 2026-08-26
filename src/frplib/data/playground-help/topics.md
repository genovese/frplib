Calling `info()` in the playground will start the interactive help
system. You will be given a set of topics, arranged hierarchically,
and you can navigate through the topic keys by moving (with arrow
keys or C-n/C-p) or by typing to do a fuzzy search on the nodes at
the current level. Hitting enter when on a node will open that node,
either a subtree or a document. The `Go Back` node will take you to
a higher level in the hierarchy.

In addition, if you pass info() a function or object from the
playground, it will attempt to display guidance on an appropriate
topic. For example, `info(uniform)`.

In addition, `info` accepts a topic string (in quotes) as an
argument. If it is an exact topic key (see below for a list), you
will be shown that document. Otherwise, that string will be used as
an initial search key to narrow the list of topics at the top level.
There is generally no need to use or remember the full keys.

You can also use Python's built-in help to get usage documentation
on any function, like `help(uniform)`. This will get the info
document if available. To force the native help function pass `True`
as the second argument, e.g., `help(uniform, True)`.

A full topic name is formed by joining the names at every level
with `::` along the path from the root to the node of interest.

Full Topic Keys
---------------
