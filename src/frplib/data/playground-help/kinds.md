# Kinds

Kinds are represented by a distinct type of object with a variety of
operation (topic: *kind-combinators*), factories (topic:
*kind-factories*), and several actions (`unfold`, `FRP.sample`,
topic: *actions*). Kinds can be transformed directly by statistics,
either with `psi(k)` or `k ^ psi`.

When printed out, kinds display the tree in canonical form. Use
`unfold` on the kind to see the unfolded tree in the
multi-dimensional case.

You can produce an FRP from a kind with `frp`.
