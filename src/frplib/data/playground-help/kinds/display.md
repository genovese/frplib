# Kind Display

[*NOTE*: The functios decribed here are expected to be included
in version 0.3.4, coming soon. Until then, the function `unfold`
is a simpler version of `unfolded`.]

By default, Kinds display in the playground as horizontal trees in
canonical form (width 1, weights normalized to 1, sorted leaves). It
can be useful to see a Kind in different forms, including unfolded
with the original weights.  There are four functions that set
the display mode for a particular format. (But see Note below.)

If `k` is a Kind, then

+ `canonical(k)` returns that Kind set to diplay in the playground in
  canonical form.

+ `unnormalized(k)` returns that Kind set to display in the playground
  with width 1 but the original unnormalized weights.

+ `unfolded(k)` returns that Kind set to display in the playground
  with full width and normalized weights.

+ `raw(k)`  returns that Kind set to display in the playground
  with full width and the original unnormalized weights.
  

*Note*: After operations like transformations or more than a few joins,
the information required to produce the `raw` form is no longer kept
to prevent undue computational cost from those operations. So `raw`
is intended for examining Kinds early in their "lifecycle".
