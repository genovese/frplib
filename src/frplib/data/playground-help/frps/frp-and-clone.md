# FRP Constructors

## Generating FRPs from Kinds

+ `frp(x)` :: Returns a fresh FRP specified by `x`, which is
     typically a Kind but can be an FRP (only the Kind of which is
     used). The returned FRP is independent of any other previously
     generated FRPs

## Cloning FRPs

A **clone** of an FRP is an independent FRP with the same Kind.

+ `clone(X)` :: produces a copy of its argument `X` if possible; primarily useful with
    FRPs and conditional FRPs, where it produces fresh copies with their own values.
    The clone is guaranteed to be independent of `X` and other clones.

