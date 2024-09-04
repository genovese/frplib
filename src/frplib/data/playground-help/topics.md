Playground help is available for the general topics listed below. In
addition, if you pass info() a function or object from the playground,
it will attempt to display guidance on an appropriate topic. For
example, `info(uniform)`. Keep in mind you can also use Python's
built-in help to get usage documentation on any function, like
`help(uniform)`, though you should probably try `info` first.

In addition, `info` accepts a topic string (in quotes) as an argument.
The top-level topics are:

General Topics
--------------
+ overview
+ actions
+ frps
+ frp-combinators
+ frp-factories
+ kinds
+ kind-combinators
+ kind-factories
+ statistics
+ statistic-builtins
+ statistic-combinators
+ statistic-factories
+ projections
+ utilities
+ modules
+ object-index

These topics are hierarchically organized, and many have
sub-topics with seperate info pages. Each topic's page
lists the available sub-topics derived from it.

A sub-topic name is formed by joining the topic name to the sub-topic
with `::`. For example, `kinds::factories::uniform` gives details on
the `uniform` factory. (Incidentally, this is the same page you get
if you call `info(uniform)` on the `uniform` function directly.)



