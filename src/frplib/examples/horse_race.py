#
# Jockeying for the Win example in Chapter 0, Section 5
#

from frplib.frps       import frp, conditional_frp
from frplib.kinds      import (conditional_kind, weighted_as)

kind_T = weighted_as(0, 1, 2, 3, weights=[0.1, 0.2, 0.4, 0.3])
kind_W = conditional_kind({
    0: weighted_as(1, 2, ..., 8, weights=[0.28, 0.18, 0.12, 0.11, 0.10, 0.08, 0.08, 0.05]),
    1: weighted_as(1, 2, ..., 8, weights=[0.06, 0.07, 0.12, 0.05, 0.08, 0.14, 0.24, 0.24]),
    2: weighted_as(1, 2, ..., 8, weights=[0.05, 0.03, 0.19, 0.48, 0.10, 0.04, 0.06, 0.05]),
    3: weighted_as(1, 2, ..., 8, weights=[0.14, 0.12, 0.18, 0.14, 0.10, 0.02, 0.12, 0.18]),
})

T = frp(kind_T)
W = conditional_frp(kind_W)
