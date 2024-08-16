# Markov Decryption Example from Section 6

__all__ = ['make_cipher', 'markov_decrypt', 'cipher1', 'clear1']

import math

from typing            import Callable, Union

from frplib.exceptions import InputError
from frplib.frps       import frp
from frplib.kinds      import ordered_samples, weighted_as
from frplib.utils      import clone

_CHARS = [
    ' ', 'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z',
]
_N_CHARS = len(_CHARS)
_END_MARK = _CHARS[0]  # Spaces, bos, and eos are treated as equivalent

# CITATION: The table _BIGRAM_LLIKE is derived from data produced
# by Peter Norvig, see http://....
# ATTN

_BIGRAM_LLIKE: dict[tuple[str, str], float] = {
    # ATTN:MISSING  # Process data tables
}

def make_cipher(substitution: Union[str, list[str]]) -> tuple[Callable[[str], str], Callable[[str], str]]:
    """Creates encryption and decryption functions for a specified substitution.

    Parameter `substitution` should be either a string or an array of single characters
    that contains a permutation of a space and the 26 capital English letters.

    Returns a tuple of functions str -> str: (encrypt, decrypt).

    """
    if isinstance(substitution, str):
        substitution = [c for c in substitution]

    if not all(c1 == c2 for c1, c2 in zip(_CHARS, sorted(substitution))):
        raise InputError('make_cipher requires a permutation of space and 26 capital letters')

    _enc = { c1: c2 for c1, c2 in zip(_CHARS, substitution) }
    _dec = { c2: c1 for c1, c2 in zip(_CHARS, substitution) }

    def encrypt(clear_text: str) -> str:
        return ''.join([_enc[c] for c in clear_text])

    def decrypt(cipher_text: str) -> str:
        return ''.join([_dec[c] for c in cipher_text])

    return (encrypt, decrypt)

def _log_like(text):
    ell = _BIGRAM_LLIKE[(_END_MARK, text[0])]

    for ind in range(_N_CHARS - 1):
        ell += _BIGRAM_LLIKE[(text[ind], text[ind + 1])]

    ell += _BIGRAM_LLIKE[(text[_N_CHARS - 1], _END_MARK)]

    return ell

def _occurs(event):
    return event.value[0] == 1

# ATTN: maybe allow n_best=1 and keep that many best states and scores
# when ==1 just return a single best, else a list of best in order

def markov_decrypt(cipher, iter=1000):
    state = _CHARS[:]
    best_score = _log_like([c for c in cipher])
    best_state = state[:]

    pair = frp(ordered_samples(2, list(range(_N_CHARS))))

    score = best_score
    for _ in range(iter):
        a, b = clone(pair).value
        candidate = state[:]
        candidate[a], candidate[b] = candidate[b], candidate[a]
        decrypt = { c2: c1 for c1, c2 in zip(_CHARS, candidate) }

        cand_score = _log_like([decrypt[c] for c in cipher])
        p = min(1, math.exp(cand_score - score))

        if p >= 1 or _occurs(frp(weighted_as(0, 1, weights=[1 - p, p]))):
            score = cand_score
            state = candidate

            if score > best_score:
                best_score = score
                best_state = state[:]

    decrypt = { c2: c1 for c1, c2 in zip(_CHARS, best_state) }
    decrypted = ''.join([decrypt[c] for c in cipher])

    return (decrypted, best_state, best_score)


# Simple Examples

cipher1 = 'QXYVE WMAVDOCBJVLCKVP TGYFVCHYOVQXYVRUSNVFCI'
clear1 = 'THE QUICK BROWN FOX JUMPED OVER THE LAZY DOG'
