from __future__ import annotations

import pytest

from frplib.expectations import E
from frplib.kinds        import weighted_as
from frplib.symbolic     import simplify, symbol

def test_symbolic_E():
    p = symbol('p')
    k0 = weighted_as(-1, 0, 1, weights=[1, p, p**2])
    assert E(k0).raw == simplify((p**2 - 1) / (1 + p + p**2))  # tests fix of Bug 20
