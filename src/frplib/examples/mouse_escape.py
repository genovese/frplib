# Mouse Escape Example from Chapter 0 Section 8

__all__ = ['initial_state', 'move', 'escaped',
           'initial_state_alt', 'move_alt', 'mouse_outcome',
           'escaped_alt']

from frplib.expectations import E
from frplib.frps         import evolve
from frplib.kinds        import conditional_kind, constant, either
from frplib.statistics   import __, Proj


# First Approach

initial_state = constant(0)
move = conditional_kind({  # type: ignore
    0: either(0, 1, 2),
    1: either(0, 2, 2),
    2: either(1, 3, 2),
    3: constant(3)
})

state = initial_state
for _ in range(16):
    state = move // state
escaped = E(state ^ (__ == 3))


# Alternative Approach

initial_state_alt = constant(0, 0)

@conditional_kind
def move_alt(attempts_and_step):
    n_attempts, step = attempts_and_step

    # If we are at the end, stay there
    if step == 3 or step == -1:
        return constant(attempts_and_step)

    n = n_attempts + 1

    # If the cat is here, last chance
    if n_attempts == 16:
        if step < 2:
            return constant(n_attempts, -1)
        else:
            return either((n, -1), (n, 3), 2)

    # From step 0, we either stay or move up
    if step == 0:
        return either((n, 0), (n, 1), 2)

    # Otherwise, we move up or down
    return either((n, step - 1), (n, step + 1), 2)

mouse_outcome = evolve(initial_state_alt, move_alt, 16)   # type: ignore
escaped_alt = E(mouse_outcome ^ (Proj[2] == 3))
