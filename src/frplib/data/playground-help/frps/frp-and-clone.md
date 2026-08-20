# FRP Constructors

## Generating FRPs from Kinds

+ `frp(x)` :: ATTN


## Cloning FRPs

A **clone** of an FRP is an independent FRP with the same Kind.

+ `clone(X)` :: produces a copy of its argument `X` if possible; primarily useful with
    FRPs and conditional FRPs, where it produces fresh copies with their own values.

