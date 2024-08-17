# Elevator Stops Example in Chapter 0 Section 8

from frplib.kinds        import Kind, conditional_kind, constant, uniform, weighted_as
from frplib.statistics   import Statistic, statistic, Sum
from frplib.vec_tuples   import as_vec_tuple

def passengers_kind(p, mu):
    pvalues = list(range(p + 1))

    weights = [1] * (p + 1)
    w = 1
    for k in pvalues[1:]:
        weights[k] = w
        w *= mu / k

    return weighted_as(pvalues, weights=weights)

def visited_floors(top_floor: int) -> Statistic:
    "Returns a statistic converting a list of floor choices to a set."
    @statistic(name=f'visited_floors<{top_floor}>')
    def visited_set(value):
        "returns the set of unique components in a fixed range, as a bit string"
        bits = [0] * top_floor
        for x in value:       # values are floors in 1, 2, ..., top_floor
            bits[x - 1] = 1   # this floor's button has been pushed
        return as_vec_tuple(bits)
    return visited_set

def union_visited(top_floor: int) -> Statistic:
    "Returns a statistic that unions two `top-floor` sets as bit-strings."
    @statistic(name=f'union<{top_floor}>', monoidal=as_vec_tuple([0] * top_floor))
    def union(value):
        "unions two `top_floor`-length bit strings into one with a bitwise-or"
        return as_vec_tuple(value[i] | value[i + 10] for i in range(top_floor))
    return union

# Main analysis

def elevator_stops(max_floor=10, p=21, mu=5) -> Kind:
    as_set: Statistic = visited_floors(max_floor)  # Statistic: convert floors to visited sets
    union: Statistic = union_visited(max_floor)    # Statistic: Union of two sets as 10-bit strings

    passenger_floor = uniform(1, 2, ..., max_floor)
    choice = as_set(passenger_floor)  # Kind for each floor choice as set

    # Kind of visited floor set for each # passengers.
    floors: dict[int, Kind] = {0: constant([0] * max_floor), 1: choice, 2: union(choice * choice)}
    for i in range(2, p):
        floors[i + 1] = union(floors[i] * floors[1])
    visited = conditional_kind(floors)  # type: ignore

    number_passengers = passengers_kind(p, mu)
    number_visited_floors = Sum(visited) // number_passengers

    return number_visited_floors
