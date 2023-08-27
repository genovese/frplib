from pygments.lexer import RegexLexer
from pygments.token import (
    Punctuation,
    Operator,
    Other,
    Token,
    Whitespace,
)

from frplib.numeric import numeric_re, integer_re

class MarketCommandLexer(RegexLexer):
    name = 'MarketCommand'
    tokens = {
        'root': [
            (r'\b(?:demo|buy|show|compare)', Token.Command),
            (r'(?:with)', Token.Connective),
            (r'(?:kind)', Token.Kind),
            (r'[@.]', Operator),
            (r'[()]', Punctuation, 'kind'),
            (integer_re, Token.Count),
            (r'\s+', Whitespace),
            (r'.', Other),
        ],
        'kind': [
            (fr'<(?:{numeric_re}(?:\s*,\s*{numeric_re})*)?>', Token.Node),
            (r'[(]', Punctuation, '#push'),
            (r'[)]', Punctuation, '#pop'),
            (numeric_re, Token.Weight),
        ],
    }
