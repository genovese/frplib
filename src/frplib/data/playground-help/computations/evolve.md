# evolve

This evolves a random system over a specified number of steps, updating
the state at each step. 

The full signature is
```
    evolve(start_state, next_state, n_steps = 1, transform=None)
```
where `start_state` represents the starting state, `next_state` 
determines transitions to the next state given the current state, and
the process is evolved `n_steps` times. Returns the representation of
state after the specified number of steps.

This can be used to produce Kinds or FRPs:

+ When `start_state` is a Kind and `next_state` is a conditional Kind,
  the returned value is the Kind of the FRP representing the state
  after `n_steps` steps.

+ When `start_state` is an FRP and `next_state` is a conditional
  FRP, the returned value is the FRP representing the state after
  `n_steps` steps. In this case, you will almost certainly want the
  conditional FRP to be constructed with `auto_clone=True` to ensure
  that the FRPs produced at each transition are distinct and
  independent.

The most common use cases for the transform argument are (i) to
apply clean() to Kinds where large numbers of branches with
negligible weight slow down the computation over many steps,
and (ii) to apply FRP.activate to the updated state to prevent
building up too large of an unevaluated FRP expression for a
fresh FRP.

The latter issue arises because fresh FRPs internally maintain
an abstract form of the expression that generated them so that
related FRPs can be co-activated. Over sufficiently large
simulations, these internal expressions can grow large enough
to exceed Python's recursion limit. The solution is to
activate the intermediate FRPs, which prevents large expressions.
Passing FRP.activate as the transform argument solves this problem.
Alternatively, if n_steps is bigger than the evolution threshold
(`environment.frp_params['evolution_threshold']`, default 128),
the intermediate (but not the last) FRP will be activated
automatically. It is generally preferable to use the automatic
solution, but when a transform argument is given, this automatic
activation does not occur.

Examples:

+ If init is the Kind of the initial state and transition is the
  conditional Kind of the next state given the initial state,
  then
  ```
      evolve(init, transition, 100)
  ```
  gives the Kind of the state after 100 steps.

+ As in the last item, `evolve(init, transition, 100, transform=clean)`
  will eliminate branches with very small weights that can
  dominate the calculations in some cases.

+ If start is an FRP and moves is a conditional FRP of the next
  state given the current state, then
  ```
      evolve(start, moves, 1000)
  ```
  gives the FRP representing the state after 1000 moves. Because
  1000 is large, the returned FRP will be fresh, but the intermediate
  join FRPs (which are not seen) will not be.

+ As in the last item, `evolve(start, moves, 1000, transform=FRP.activate)`
  will activate all of the produced FRPs, including the last but
  excluding start.

+ `evolve(a, c, 200, transform=stat)`  will transform each result by
  statistic stat. Note that in this case, stat must preserve or
  create the structure expected by c.

