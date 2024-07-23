#
# Traffic Light from A Dialogue on Systems and State
#

from enum import IntEnum

from frplib.frps       import conditional_frp, frp
from frplib.exceptions import FrplibException
from frplib.kinds      import Kind, conditional_kind, constant, uniform, weighted_as
from frplib.statistics import Fork, Id
from frplib.utils      import clone

class TrafficLight(IntEnum):
    GREEN = 0
    YELLOW = 1
    RED = 2

    def __next__(self):
        match self:
            case TrafficLight.GREEN:
                return TrafficLight.YELLOW
            case TrafficLight.YELLOW:
                return TrafficLight.RED
            case TrafficLight.RED:
                return TrafficLight.GREEN

# First Effort

change_on = {
    TrafficLight.GREEN:  1 / 30,
    TrafficLight.YELLOW: 1 / 5,
    TrafficLight.RED:    1 / 30,
}

@conditional_frp
def tick_light(state):
    color, ticks = state
    change_probability = change_on[color]

    next_kind = weighted_as(
        (color, ticks + 1),
        (next(color), 0),
        weights=[1 - change_probability, change_probability]
    )
    return frp(next_kind)

# Provisional
@conditional_kind
def tick_light_kind(state):
    color, ticks = state
    change_probability = change_on[color]

    return weighted_as(
        (color, ticks + 1),
        (next(color), 0),
        weights=[1 - change_probability, change_probability]
    )

start_any_color = uniform(change_on.keys()) ^ Fork(Id, 0)
start_green = constant(TrafficLight.GREEN, 0)

def n_ticks(n, InitialState):
    assert n >= 0, "Number of ticks must be non-negative."

    if isinstance(InitialState, Kind):
        InitialState = frp(InitialState)

    State = InitialState
    for _ in range(n):
        State = clone(tick_light) // State

    return State

# Provisional
def n_ticks_kind(n, initial_state):
    assert n >= 0, "Number of ticks must be non-negative."

    state = initial_state
    for _ in range(n):
        state = tick_light_kind // state

    return state


# Graph Example

def neighbors(n: int) -> list[int]:
    # Ordinarily would use a dict but this matches the text
    match n:
        case 1:
            return [2, 3, 4, 5, 8]
        case 2:
            return [1, 3, 4]
        case 3:
            return [1, 2]
        case 4:
            return [1, 2]
        case 5:
            return [1, 6]
        case 6:
            return [5, 8]
        case 7:
            return []
        case 8:
            return [6, 1]
        case _:
            raise FrplibException("Invalid node in graph example")

@conditional_kind
def next_node(node):
    adjacent = neighbors(node)
    if len(adjacent) == 0:
        return constant(node)
    return uniform(adjacent)

def random_walk(start, n_steps: int = 1):
    assert n_steps >= 0, "Number of steps must be >= 0."

    current = start
    for _ in range(n_steps):
        current = next_node // current

    return current

@conditional_kind
def next_node_visit8(state):
    "Version of next_node that tracks whether we visited node 8."
    node, visit, time = state
    adjacent = neighbors(node)
    if len(adjacent) == 0:
        return constant(state)

    node_kind = uniform(adjacent)
    if visit == 1:
        return node_kind ^ Fork(Id, visit, time)
    if node == 8:
        return node_kind ^ Fork(Id, 1, time + 1)
    return uniform(adjacent) ^ Fork(Id, 0, time + 1)
