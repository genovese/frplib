from __future__ import annotations

import pytest

from frplib.frps       import frp
from frplib.kinds      import uniform
from frplib.statistics import __
from frplib.utils      import dim

def test_empty_conditional():
    X = frp(uniform(1, 2, ..., 8))
    a = X.value
    Y = X | (__ < a)
    Z = X | (__ <= a)

    assert dim(Y) == 0
    assert Z.value == X.value
