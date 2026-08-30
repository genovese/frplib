# Kinds

A Kind embodies our knowledge about the value of an FRP.
Every FRP has a Kind, and FRPs with the same Kind
behave similarly.

A Kind is a rooted tree with values at the nodes
and numbers on the edges and that satisfies
four rules:

+ *Completeness Rule*: every path from root to leaf has the *same length*.

+ *Level Rule*: all the nodes within each level of the tree must hold
  *distinct* values of the *same dimension and type*.

+ *Prefix Rule*: on every path from root to leaf, each node is a
  *strict prefix* of every node later on the path.
  
+ *Positivity Rule*: all weights are *positive*.

We display these trees horizontally.

In `frplib`, a Kind is a distinct type of object with a variety of
methods and operations that apply to it. We use Kinds to build
random systems by combining simpler Kinds into more complicated
ones.

We usually use lowercase names for Kinds.

The expectation of a Kind `k` is found with `E(k)`.
