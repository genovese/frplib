# CITATION: The table BIGRAM_FREQS is derived from data produced
# by Peter Norvig, see http://norvig.com/google-books-common-words.txt

import re
import math

from collections         import defaultdict
from pathlib             import Path
from typing              import cast


__all__ = ['BIGRAM_FREQS']

_CHARS = [
    ' ', 'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z',
]
_N_CHARS = len(_CHARS)
_END_MARK = _CHARS[0]  # Spaces, bos, and eos are treated as equivalent
_LBASELINE = -20.0     # Default log proportion for missing bigrams

def _process_word_counts() -> dict[tuple[str, str], float]:
    word_file = Path('google-books-common-words.txt')

    bigram_freqs: dict[tuple[str, str], int] = defaultdict(int)
    with open(word_file, 'r') as f:
        for line in f:
            m = re.match(r'\s*([A-Z]+)\s+([0-9]+)\s*$', line, re.IGNORECASE)
            if m:
                word = m.group(1)
                count = int(m.group(2))
            
                char1 = _END_MARK
                for char2 in word:
                    bigram_freqs[(char1, char2)] += count
                    char1 = char2
                bigram_freqs[(char1, _END_MARK)] += count
                
    total = 0
    for cnt in bigram_freqs.values():
        total += cnt

    for c1 in _CHARS:
        for c2 in _CHARS:
            bigram = (c1, c2)
            if bigram in bigram_freqs:
                bigram_freqs[bigram] = math.log(bigram_freqs[bigram] / total)    # type: ignore
            else:
                bigram_freqs[bigram] = _LBASELINE                                # type: ignore
                
    return cast(dict[tuple[str, str], float], bigram_freqs)

BIGRAM_FREQS: dict[tuple[str, str], float] = _process_word_counts()

if __name__ == '__main__':
    print('''# CITATION: The table BIGRAM_FREQS is derived from data produced
# by Peter Norvig, see http://norvig.com/google-books-common-words.txt
#
# These contain log proportions of bigrams in a large Google word corpus.
# We mark beginning of string/word and end of string/word with ' ' in
# the bigram pairs.
#
# Only capital letters and space (bos/bow/eos/eow) are included.
#
''')

    print('BIGRAM_LLIKE = {')
    for k, v in BIGRAM_FREQS.items():
        print(f'    {k}: {v},')
    print('}')
