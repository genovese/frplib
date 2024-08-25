#
# Random Points in a Circle Example Chapter 0, Section 4.3
# Points in a Circle, With Constraints Example Chapter 0, Section 5
#
from math              import floor
from typing            import Literal, Union

from frplib.frps       import FRP, frp
from frplib.kinds      import (conditional_kind,
                               constant, uniform, weighted_by)
from frplib.utils      import compose, dim, irange


#
# Helpers
#

def y_points(x: int, radius: Union[int, float] = 5) -> list[int]:
    r = abs(radius)
    r_lo = floor(r)
    return [y for y in irange(-r_lo, r_lo) if y * y <= r * r - x * x]

num_y_points = compose(len, y_points)   # len `after` y_points

def points_inside(radius: Union[int, float] = 5) -> list[tuple[int, int]]:
    "Returns list of integer points within circle of given radius >= 0"
    r = abs(radius)
    r_lo = floor(r)
    vals = list(irange(-r_lo, r_lo))
    return [(x, y) for x in vals for y in vals
            if x * x + y * y <= r * r]


#
# FRP Factories
#

def circle_points(
        radius: Union[int, float] = 5,
        method: Literal["mixture", "jointly"] = "mixture"
) -> FRP:
    "Returns FRP for uniform random point inside circle of a given radius."
    if method == "jointly":
        return frp(uniform(points_inside(radius)))

    # Construct as a mixture
    r = abs(radius)
    r_lo = floor(r)
    if r == 0:
        return frp(constant(0, 0))

    x_kind = weighted_by(-r_lo, -r_lo + 1, ..., r_lo, weight_by=num_y_points)

    @conditional_kind(domain=irange(-r_lo, r_lo), target_dim=1)   # type: ignore
    def y_kind(x):
        return uniform(y_points(x))

    return frp(x_kind >> y_kind)
