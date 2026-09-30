"""Alice and Bob chatting over a wire

Two different communication channels and two different strategies
for efficiently transmitting information.

"""
# pylint: disable=invalid-name

import math

from collections.abc   import Iterable, Sequence
from typing            import Literal

import numpy as np

from frplib.frps       import force_unkinded, frp, frp_factory
from frplib.kinds      import binary
from frplib.quantity   import from_numpy, as_quant_vec
from frplib.statistics import statistic, statistic_factory, ForEach
from frplib.vec_tuples import VecTuple

#
# Random Bits
#

@frp_factory
def random_bits(n: int, p=0.5):
    "produces n random bits with specified probability p on 1."
    X = frp(binary(p))
    if n > 8:
        X = force_unkinded(X)
    return X ** n

@statistic_factory
def add_noise_to(y0):
    """adds random binary noise to the given tuple"""
    y = as_quant_vec(y0)
    n = len(y)

    @statistic(codim=n, dim=n)
    def add_noise(noise):
        return (y + noise) % 2

    return add_noise

#
# Binary Symmetric Channel (noisy)
#

@statistic_factory
def repetition_encode(r: int):
    """repeats each input bit a fixed number of times"""

    @statistic(codim=1, dim=r)
    def rep_r(b):
        return [b] * r

    rep_code = ForEach(rep_r)
    rep_code.name = f'repetition{r}_encode'
    rep_code.doc = f'encodes its input with a repetition-{r} code'
    return rep_code

@statistic_factory
def repetition_decode(r: int):
    """repeats each input bit a fixed number of times

    r should be an odd, positive integer.

    """

    @statistic(codim=r, dim=1)
    def majority_rule_r(bs):
        if sum(bs) > r // 2:
            return 1
        return 0

    rep_code = ForEach(majority_rule_r, by=r)
    rep_code.name = f'repetition{r}_decode'
    rep_code.doc = f'decodes its input with a repetition-{r} code'
    return rep_code

# Hamming(7,4) generator (G) and parity-check (H) matrices

G = np.array([
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1]
], dtype=np.int64)

H = np.array([
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1]
], dtype=np.int64)


@statistic
def hamming_7_4_encode(raw_bits):
    """encodes its input with a Hamming(7, 4) code"""

    hamming = ForEach(lambda u: from_numpy((u @ G) % 2), by=4)
    return hamming(raw_bits)

@statistic
def hamming_7_4_decode(encoded_bits):
    """decodes its input with a Hamming(7, 4) code"""

    @statistic(codim=7, dim=4)
    def decode_block(block):
        decoded = list(block)
        s = (block @ H.T) % 2
        s_matches = (H.T == s).all(axis=1)

        if s_matches.any():
            correct = np.argmax(s_matches)
            decoded[correct] = 1 - decoded[correct]

        return decoded[:4]

    hamming = ForEach(decode_block, by=7)
    return hamming(encoded_bits)


#
# Bandwidth-Limited Channel (negligible noise)
#

def to_unary(n: int) -> list[Literal[0, 1]]:
    "Converts an natural number to its unary representation, counting 1s followed by a 0."
    return [1] * n + [0]  # type: ignore

def from_unary(bits: Iterable[Literal[0, 1]]) -> int:
    "Converts the unary representation of a natural number to the number itself."
    q = 0
    for b in bits:
        if b == 0:
            break
        q += 1
    return q

def to_binary_rev(n, width=8) -> list[Literal[0, 1]]:
    "Converts a natural number to reversed (LSB-first) binary representation of specified width."
    v = n
    digits = []
    for _ in range(width):
        digits.append(v % 2)
        v >>= 1

    if v > 0:
        raise ValueError(f'in_binary: cannot convert number {n} bigger than width {width} allows')

    return digits

def to_binary(n, width=8) -> list[Literal[0, 1]]:
    """Converts an integer to a list of binary digits with specified width."""
    return list(reversed(to_binary_rev(n, width)))  # ATTN: improve

def from_binary_rev(bits: Iterable[Literal[0, 1]]) -> int:
    "Converts reversed (LSB-first) binary representation to a natural number"
    n = 0
    exp = 1
    for x in bits:
        n += x * exp
        exp <<= 1

    return n

def from_binary(bits: Sequence[Literal[0, 1]], width=8) -> int:
    """Converts a list of binary digits with specified width to an integer."""
    return from_binary_rev(reversed(bits[:width]))  # ATTN: improve

def to_golomb(n: int, m: int, b: int) -> list[Literal[0, 1]]:
    """Golomb encodes an integer `n` with parameter `m` of `b` bits."""
    q = n // m
    r = n % m

    encoded = to_unary(q)
    offset = 2 ** (b + 1) - m

    if r < offset:
        encoded.extend(to_binary(r, width=b))
    else:
        encoded.extend(to_binary(r + offset, width=b + 1))

    return encoded

def from_golomb(bits: Sequence[Literal[0, 1]], m: int, b: int) -> tuple[int, Sequence[Literal[0, 1]]]:
    """Golomb decodes a bit string to produce an integer and remaining bit string."""
    q = from_unary(bits)
    r0 = from_binary(bits[(q + 1):], width=b)
    offset = 2 ** (b + 1) - m

    if r0 < offset:
        return (q * m + r0, bits[(q + 1 + b):])

    r = from_binary(bits[(q + 1):], width=b + 1) - offset
    return (q * m + r, bits[(q + 1 + b + 1):])

def run1s_lengths(bits: Sequence[Literal[0, 1]]) -> tuple[list[int], Literal[0, 1]]:
    """Computes run lengths of 1s and final bit from a bit string. 00 means run of len zero."""
    lengths = []
    ell = 0
    for b in bits:
        if b == 0:
            lengths.append(ell)
            ell = 0
        else:
            ell += 1

    if ell > 0:
        lengths.append(ell)
        return (lengths, 1)
    return (lengths, 0)

@statistic
def RunLengths(bits):
    """the lengths of runs of 1s and the final bit in a binary input tuple"""
    lens, last = run1s_lengths(bits)
    return VecTuple.join(lens, last)

@statistic_factory
def golomb_encode(p=0.9):
    "encodes a bit string with a Golomb code for the specified p."
    m = math.ceil(-1.0 / math.log2(p))
    b = math.floor(math.log2(m))
    w = math.ceil(math.log2(b + 1))  # Width of m in lg scale

    @statistic
    def GolombEncode(bits):
        encoded = to_binary_rev(w, width=3)
        encoded.extend(to_binary_rev(m, width=2 ** w))

        runs, last = run1s_lengths(bits)
        for run in runs:
            encoded.extend( to_golomb(run, m, b) )

        encoded.append(last)
        return encoded

    GolombEncode.doc = f'encodes a bit string with a Golomb code for p={p}'

    return GolombEncode

@statistic
def golomb_decode(encoded):
    "decodes a Golomb code"
    w = from_binary_rev(encoded[:3])
    hi = 3 + 2 ** w
    m = from_binary_rev(encoded[3:hi])
    b = math.floor(math.log2(m))

    runs: list[int] = []
    rest = encoded[hi:]
    while rest:
        if len(rest) == 1:  # end bit
            if rest[0] == 1:
                runs[-1] *= -1   # mark missing 0
            break
        run, rest = from_golomb(rest, m, b)
        runs.append(run)

    decoded = []
    for run in runs:
        if run < 0:
            decoded.extend([1] * (-run))
        else:
            decoded.extend([1] * run + [0])

    return decoded

# def golomb_decode(p=0.9) -> Statistic:
#     "Returns a statistic that decodes a Golomb code for the specified p."
#     m = math.ceil(-1.0 / math.log2(p))
#     b = math.floor(math.log2(m))
#     w = math.ceil(math.log2(b + 1))  # Width of m in lg scale
#
#     return GolombDecode
