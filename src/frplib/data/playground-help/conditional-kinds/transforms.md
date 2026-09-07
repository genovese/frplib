# Transforms of Conditional Kinds

Because Conditional Kinds return Kinds for each input value, we can
transform them by statistics. There are three methods for doing
these transforms.

If `C` is a Conditional Kind of type 'm -> m + n', then

+ `C.transform_targets(psi)` creates a Conditional Kind of type
  `m -> m + p` where `psi` is a statistic of type `n -> p`. This
  transforms the *targets only* with the statistic `psi`.
  `psi` must be compatible with all the targets.

+ `C.transform_joined(phi)` creates a Conditional Kind of type
  `m -> m + r` where `phi` is a statistic of type `m + n -> r`.
  This transforms the *joined only* with the statistic `phi`.
  `psi` must be compatible with all the joined Kinds.

+ `C.transform(psi)` is equivalent to `C.transform_targets(psi)`.
