# Six of One, Equilateral of the Other Example in Chapter 0 Sec 8

__all__ = ['vertices', 'is_equilateral', 'equilateral', 'vertex_dists',
           'side_lengths', 'heron', 'Q_kind', 'A_kind',]

from frplib.exceptions   import EvaluationError
from frplib.kinds        import clean, without_replacement
from frplib.numeric      import numeric_abs, numeric_sqrt
from frplib.statistics   import statistic, scalar_statistic, Diff, Sqrt
from frplib.utils        import irange

vertices = without_replacement(3, irange(1, 6))

is_equilateral = Diff == (2, 2)
equilateral = is_equilateral(vertices)

vertex_dists = [0, 1, numeric_sqrt(3), 2, numeric_sqrt(3), 1]

@statistic
def side_lengths(triangle):
    return [vertex_dists[int(numeric_abs(triangle[i] - triangle[(i - 1) % 3]))] for i in range(3)]

@scalar_statistic
def heron(a, b, c):
    s = (a + b + c) / 2
    z = s * (s - a) * (s - b) * (s - c)
    if z < 0:
        raise EvaluationError(f'Side lengths do not form a triangle: {a}, {b}, {c}')
    return Sqrt(z)

Q_kind = equilateral
A_kind = clean(vertices ^ side_lengths ^ heron)
