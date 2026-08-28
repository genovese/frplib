# kind

`kind` is a smart constructor for Kinds that can create a Kind
from a variety of input. This is the basis method for constructing
a Kind from any other appropriate object, including an FRP.
It can also be used as a decorator to define a Kind via a procedure.

The signature is `kind(spec)` where `spec` is a specification
that describes a Kind. It can be one of the following:

+ **An FRP**: Extracts or computes the FRP's Kind, as needed.

+ **A Kind**: In this case, the Kind itself is just returned.

+ Any object with a `.kind` property or a `.kind_of` method.

+ A string in sexp format. See "Sexp string format for Kind"
  below.

+ Any falsy object produces the empty Kind, `Kind.empty`.

In addition, if `spec` has a `.conditional_kind_of` method,
then `kind` will return the resulting conditional Kind.
This works, for instance, with conditional FRPs
and conditional Kinds. When applied to a conditional Kind, its
input is returned unchanged.

Examples

+ `kind(frp(uniform(1, 2, 3)))` => is the Kind `uniform(1, 2, 3)`
+ `kind(uniform(1, 2, 3))` => is the Kind `uniform(1, 2, 3)`
+ `kind("(<> 1 <0> 1 <1>)")` => is equivalent to `choice(0, 1)`

## Procedure Decorator

`kind` can also be used as a decorator on a generator or on a function
returning a Kind. These functions should have no arguments without
default values. These ***do not return functions***. Rather, they
use the functions or generators to produce a Kind, and the name
of the function in the `def` is the name of the variable the Kind
is bound to.

For example
```python
    @kind
    def x_plus_y():
        x = yield k_x
        y = yield k_y
        return x + y
```
This sets `x_plus_y` to a Kind that is
equal to `(k_x * k_y) ^ Sum`. See the info
document *Kinds::Kind Procedures* for detail.


## Sexp string format for Kind

A kind tree is specified by a non-empty, ()-balanced expression,
where the outer layer of parentheses encompasses the entire specification.
Within each () pair, the string looks like
```
 (<_node_> _weight_1 _value_or_subtree_1 ...)
```
here `<_node_>` has explicit angle brackets to distinguish the
tuple values from the numeric weights. It is a comma-separated
list of numbers which can be empty. The root node of the
tree is always an empty `<>`. The specification can extend over
multiple lines, and whitespace is ignored.

Each `_value_or_subtree_k` is a node in angle brackets indicating
a leaf and giving the value at that leaf or it is another
()-balaced expression of the same form as just described.

As described in the text, the values within each subtree must be
distinct, and the nodes on any path from root to leaf must be
*consistent* in the sense that earlier nodes' numeric lists are
prefixes of later nodes' lists on that path. All leaf nodes must
also have the same dimension, and all weights must be positive.

Weights can be floating point numbers like 1.0 or 1e-7
or rational numbers like 1/7 with no space between the numbers and the /.

So,
```
    (<> 1 (<1> 2 <1, 2> 3 <1, 6>) 2 (<10> 1 <10, 20>))
```
is valid. Within each (), the nodes are disinct and
along one path we get consistent sequences <>, <1>, <1,2> or <1,6>
and on the other <>, <10>, <10, 20>.
But 
```
    (<> 1 (<1> 2 <1, 2> 3 <1, 2>) 2 (<10> 1 <10, 20>))
    (<> 1 (<1> 2 <1, 2> 3 <5, 6>) 2 (<10> 1 <10, 20>))
    (<> 1 (<1> 2 <1, 2> 3 <5, 6>) 2 (<10> 1 <10, 20, 30>))
```
are invalid. The first has two equal nodes <1, 2> in the
same subtree. The second has an inconsistent path <>, <1>,
<5, 6>. And the third has leaf nodes of different dimensions.

Examples:
+ `(<>)`
+ `(<> 1 <2> 1 <3>)`
+ `(<> 1 (<1> 1 <1, 100> 100 <1, 1>) (<4> 1/2 <4, -1> 0.01 <4, -10>) (<5> 100 <-1, -1>))`
