# Six of One, Equilateral of the Other Example in Chapter 0 Sec 8

__all__ = ['vertices', 'is_equilateral', 'vertex_dists',
           'side_lengths', 'heron', 'T_kind', 'A_kind',]

from frplib.kinds        import clean, without_replacement
from frplib.numeric      import numeric_abs, numeric_sqrt
from frplib.statistics   import statistic, Diff, Sqrt
from frplib.utils        import irange

vertices = without_replacement(3, irange(1, 6))
is_equilateral = vertices ^ (Diff == (2, 2))

vertex_dists = [0, 1, numeric_sqrt(3), 2, numeric_sqrt(3), 1]

@statistic
def side_lengths(triangle):
    return [vertex_dists[int(numeric_abs(triangle[i] - triangle[(i - 1) % 3]))] for i in range(3)]

@statistic
def heron(a, b, c):
    s = (a + b + c) / 2
    return Sqrt(s * (s - a) * (s - b) * (s - c))

T_kind = is_equilateral
A_kind = clean(vertices ^ side_lengths ^ heron)
