# Composition of Statistics

Statistics are functions and so they can be *composed*, with the output of one
statistic fed into another. This operation requires that the dimension and the
codimensions of the two statistics are compatible and that the values fed


+ `^` :: the transformation operator acts as *chained* composition (`f ^ g` is `f` ***then*** `g`)
         of statistics. Multiple functions can be combined (e.g., `f ^ g ^ h` which is
         equivalent to `Chain(f, g, h)` as described below).

   For example, `Diff ^ Sum` first computes the differences of its input and then adds them up,
   and `Diff ^ Sum ^ Abs` gives computes the differences, sums them, then take the absolute value.

   This operator can take a vector tuple (cf. `tup`) on the left side and a statistic on the right,
   so it gives a way to evaluate statistics with complicated expressions.
   For instance, `tup(10, 4, 0, -1, 5) ^ Diff ^ Sum ^ Abs` returns 5.

+ `()` :: the evaluation operator is used with statistics in multiple ways.
   If `psi` is a statistic and `v` a suitable value, the `psi(v)` evaluates the statistic at the value.
   However, it can also be used for composition, which is handy in statistic expressions.
   For instance, `phi(psi)` is the statistic `Compose(phi, psi)` or equivalently `psi ^ phi`.

+ `Compose` :: compose statistics in mathematical order. `Compose(f, g)` means `f` ***after*** `g`,
   i.e., (f o g)(x) = f(g(x)).

   This combinator takes any number of statistics and composes them with the rightmost argument
   applied first. The dimensions/codimensions and domains/codomains must be compatible.

   For instance, `Compose(f, g, h)` takes an input `v`, passes it to `h`, passes `h(v)` to `g`,
   and passes `g(h(v))` to `f`, producing `f(g(h(v)))`. The argument order is the same as that
   with which we read the functions in standard mathematical notaion.

+ `Chain` :: compose statistics in pipeline order. `Chain(f, g)` means `f` ***then*** `g`,
   i.e., (f ; g)(x) = g(f(x)).  This is the opposite of the order from `Compose`.

   This combinator takes any number of statistics and composes them with the leftmost argument
   applied first. The dimensions/codimensions and domains/codomains must be compatible.

   For instance, `Chain(f, g, h)` takes an input `v`, passes it to `f`, passes `f(v)` to `g`,
   and passes `g(f(v))` to `g`, producing `h(g(f(v)))`. The argument order is the same as that
   with which the functions are evaluated.
