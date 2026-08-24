""" Data from the discussion of Alice's deal (and Bob's spying) in Chapter 5.1.

Exports the Kind kindA, the original Kind of FRPs that Alice had ordered
before she learned Bob's observations.

"""

from frplib.kinds      import weighted_as
from frplib.quantity   import tup


# The kind of Alice's order, see Figure 17

kindA = weighted_as({
    tup(0, 0, -20): '0.025',
    tup(0, 0, -10): '0.025',
    tup(0, 1, -1):  '0.225',
    tup(0, 1,  1):  '0.225',
    tup(1, 0, -2):  '0.225',
    tup(1, 0,  0):  '0.225',
    tup(1, 1, 5):   '0.025',
    tup(1, 1, 10):  '0.025',
})
