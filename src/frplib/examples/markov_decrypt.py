# Markov Decryption Example from Section 6

__all__ = ['make_cipher', 'markov_decrypt',
           'cipher1', 'clear1', 'crypt1',
           'cipher2', 'clear2', 'crypt2']

import math
import re

from collections         import defaultdict
from pathlib             import Path
from typing              import Callable, Union, cast

from frplib.data.words   import BIGRAM_LLIKE
from frplib.exceptions   import InputError
from frplib.frps         import frp
from frplib.kinds        import without_replacement, weighted_as
from frplib.utils        import clone


_CHARS = [
    ' ', 'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z',
]
_N_CHARS = len(_CHARS)
_END_MARK = _CHARS[0]  # Spaces, bos, and eos are treated as equivalent

# CITATION: The table BIGRAM_LLIKE is derived from data produced
# by Peter Norvig, see http://norvig.com/google-books-common-words.txt

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
    n = len(text)
    ell = BIGRAM_LLIKE[(_END_MARK, text[0])]

    for ind in range(n - 1):
        ell += BIGRAM_LLIKE[(text[ind], text[ind + 1])]

    ell += BIGRAM_LLIKE[(text[n - 1], _END_MARK)]

    return ell

def _occurs(event):
    return event.value[0] == 1

def markov_decrypt(cipher, iter=1000, init=None, n_best=1):
    """Applies Markov decryption algorithm to given cipher text.

    Parameters:
    + cipher: str - The cipher text
    + iter: int [=1000] - number of iterations
    + init: list[str] | None [=None] - an initial permutation
        if not None, or the identity permutation if None.
        This must be a permutation of A-Z and ' '.
    + n_best: int [=1]: the number of best decryptions to
        keep and return (ATTN: CURRENTLY NOT USED)

    If n_best == 1, returns a dictionary containing the estimated
    clear text, the highest scoring permutation, and the best score,
    with respective keys 'clear', 'cipher', and 'score'. If n_best >
    1, return a list of such dictionaries in decreasing order of
    score.

    """
    if init is None:
        state = _CHARS[:]
    else:
        state = init[:]
    decrypt = { c2: c1 for c1, c2 in zip(_CHARS, state) }
    best_score = _log_like([decrypt[c] for c in cipher])
    best_state = state[:]

    pair = frp(without_replacement(2, range(_N_CHARS)))

    score = best_score
    for _ in range(iter):
        a, b = clone(pair).value
        candidate = state[:]
        candidate[a], candidate[b] = candidate[b], candidate[a]
        decrypt = { c2: c1 for c1, c2 in zip(_CHARS, candidate) }

        cand_score = _log_like([decrypt[c] for c in cipher])
        if cand_score >= score:
            p = 1.0
        else:
            p = math.exp(cand_score - score)

        if p >= 1 or _occurs(frp(weighted_as(0, 1, weights=[1 - p, p]))):
            score = cand_score
            state = candidate

            if score > best_score:
                best_score = score
                best_state = state[:]

    decrypt = { c2: c1 for c1, c2 in zip(_CHARS, best_state) }
    decrypted = ''.join([decrypt[c] for c in cipher])

    return {
        'clear': decrypted,
        'cipher': best_state,
        'score': best_score
    }


# Simple Examples

crypt1 = ['V', 'U', 'D', 'M', 'F', 'Y', 'L', 'I', 'X', 'W', 'P', 'A', 'R', 'T', 'J', 'C', 'G', 'E', 'O', 'Z', 'Q', ' ', 'H', 'B', 'K', 'N', 'S']
cipher1 = 'QXYVE WMAVDOCBJVLCKVP TGYFVCHYOVQXYVRUSNVFCI'
clear1 = 'THE QUICK BROWN FOX JUMPED OVER THE LAZY DOG'

crypt2 = ['V', 'U', 'D', 'M', 'F', 'Y', 'L', 'I', 'X', 'W', 'P', 'A', 'R', 'T', 'J', 'C', 'G', 'E', 'O', 'Z', 'Q', ' ', 'H', 'B', 'K', 'N', 'S']
clear2 = 'MANY THAT LIVE DESERVE DEATH AND SOME THAT DIE DESERVE LIFE CAN YOU GIVE IT TO THEM THEN DO NOT BE TOO EAGER TO DEAL OUT DEATH IN JUDGEMENT FOR EVEN THE VERY WISE CANNOT SEE ALL ENDS I HAVE NOT MUCH HOPE THAT GOLLUM CAN BE CURED BEFORE HE DIES BUT THERE IS A CHANCE OF IT AND HE IS BOUND UP WITH THE FATE OF THE RING MY HEART TELLS ME THAT HE HAS SOME PART TO PLAY YET FOR GOOD OR ILL BEFORE THE END AND WHEN THAT COMES THE PITY OF BILBO MAY RULE THE FATE OF MANY YOURS NOT LEAST'
cipher2 = 'TUJNVQXUQVRWHYVFYZYOHYVFYUQXVUJFVZCTYVQXUQVFWYVFYZYOHYVRWLYVMUJVNC VIWHYVWQVQCVQXYTVQXYJVFCVJCQVDYVQCCVYUIYOVQCVFYURVC QVFYUQXVWJVP FIYTYJQVLCOVYHYJVQXYVHYONVBWZYVMUJJCQVZYYVURRVYJFZVWVXUHYVJCQVT MXVXCGYVQXUQVICRR TVMUJVDYVM OYFVDYLCOYVXYVFWYZVD QVQXYOYVWZVUVMXUJMYVCLVWQVUJFVXYVWZVDC JFV GVBWQXVQXYVLUQYVCLVQXYVOWJIVTNVXYUOQVQYRRZVTYVQXUQVXYVXUZVZCTYVGUOQVQCVGRUNVNYQVLCOVICCFVCOVWRRVDYLCOYVQXYVYJFVUJFVBXYJVQXUQVMCTYZVQXYVGWQNVCLVDWRDCVTUNVO RYVQXYVLUQYVCLVTUJNVNC OZVJCQVRYUZQ'
