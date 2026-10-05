"""Random Points in a Circle With Observations Example 4.11 Chapter 4.4

Exports

+ y_points :: generates y coordinates of points at a given x
+ points_inside :: list of integer points in a circle of given radius
+ circle_points :: FRP factory for uniform point in a circle

"""
from math              import floor
from typing            import Literal, Union

from frplib.frps       import frp, frp_factory
from frplib.kinds      import (conditional_kind,
                               constant, uniform, weighted_by)
from frplib.utils      import compose, irange


#
# Helpers
#

def y_points(x: int, radius: Union[int, float] = 5) -> list[int]:
    """Returns the y-coordinates of points at x inside a circle of given radius."""
    r = abs(radius)
    r_lo = floor(r)
    return [y for y in irange(-r_lo, r_lo) if y * y <= r * r - x * x]

num_y_points = compose(len, y_points)   # len `after` y_points

def points_inside(radius: Union[int, float] = 5) -> list[tuple[int, int]]:
    """Returns list of integer points within circle of given radius >= 0."""
    r = abs(radius)
    r_lo = floor(r)
    vals = list(irange(-r_lo, r_lo))
    return [(x, y) for x in vals for y in vals
            if x * x + y * y <= r * r]


#
# FRP Factories
#

@frp_factory
def circle_points(
        radius: Union[int, float] = 5,
        method: Literal["join", "all"] = "join"
):
    """a uniform random point inside circle of a given radius.

    Accepts two parameters
    - radius (default: 5): the radius of the circle
    - method (default: "join"): method used to generate the points,
        either "join" or "all" as described in the text.

    """
    if method == "all":
        return frp(uniform(points_inside(radius)))

    # Construct as a join
    r = abs(radius)
    r_lo = floor(r)
    if r == 0:
        return frp(constant(0, 0))

    x_kind = weighted_by(-r_lo, -r_lo + 1, ..., r_lo, weight_by=num_y_points)

    @conditional_kind(domain=irange(-r_lo, r_lo), target_dim=1)
    def y_kind(x):
        return uniform(y_points(x))

    return frp(x_kind >> y_kind)
