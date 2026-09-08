"""Example 4.8 `Dividing the Pizza` in Chapter 4 Building with Joins

Exports:

 C_0, C_1, C_2, C_3, C_10 -- FRPs representing the choice at different stage
 F_1 -- the transition mechanism at the first stage
 F_n -- the transition mechanism at any stage

"""

from frplib.frps       import frp, conditional_frp, evolve
from frplib.kinds      import binary, constant, choice
from frplib.statistics import Proj
from frplib.utils      import clone


C_0 = frp(constant(0))
Flip = frp(choice(0, 1))

F_1 = conditional_frp({
    0: clone(Flip) * clone(Flip) ^ (2 * Proj[2] + Proj[1]),
    1: frp(constant(1)),
    2: frp(constant(2)),
    3: frp(constant(3))
})

C_1 = (C_0 >> F_1) ^ Proj[2]

F_n = conditional_frp({
    0: frp(binary() * binary()) ^ (2 * Proj[2] + Proj[1]),
    1: frp(constant(1)),
    2: frp(constant(2)),
    3: frp(constant(3))
}, auto_clone=True)

C_2 = (C_1 >> F_n) ^ Proj[2]
C_3 = (C_2 >> F_n) ^ Proj[2]

C_10 = evolve(C_0, F_n, 10)
