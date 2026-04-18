#
# A singleton environment for capturing global options in an interactive session.
#
# This controls the output formats of objects that should print in nice
# or rich ways in an interactive session. While this can be used at the
# library level, it is primarily for interactive use and not thread safe.
#
from __future__ import annotations

from dataclasses  import dataclass, field
from decimal      import Decimal, ROUND_HALF_UP
from typing       import TypedDict

from rich.console import Console
from rich.theme   import Theme

bright_theme = Theme({
    "repr.number": "#3333cc",
    "repr.number_complex": "#333366",
    "repr.bool_true": "#009933",
    "repr.bool_false": "#990033",
    "repr.str": "#330066",
    "repr.attrib_name": "#330000",
    "repr.attrib_value": "#000033",
    "markdown.item.bullet": "bold magenta",
    "markdown.item.number": "bold magenta",
    "markdown.code": "bold red on #cccccc",
})

dark_theme = Theme({
    "repr.number": "#cccc33",
    "repr.number_complex": "#cccc99",
    "repr.bool_true": "#ff66cc",
    "repr.bool_false": "#66ffcc",
    "repr.str": "#ccff99",
    "repr.attrib_name": "#ccffff",
    "repr.attrib_value": "#ffffcc",
    "markdown.code": "bold magenta on white",
    "markdown.code_block": "#4682b4 on white",
})

class FrpParams(TypedDict):
    complexity_threshold: int   # Maximum kind size to maintain kindedness
    evolution_threshold: int    # Evolution steps above which intermediate FRPs are automatically activated

def default_frp_params() -> FrpParams:
    return {
        'complexity_threshold': 16384,   # was FRP.COMPLEXITY_THRESHOLD
        'evolution_threshold':  128,     # was FRP.EVOLUTION_THRESHOLD
    }


class NumericOutParams(TypedDict):
    denom_limit: int            # Max denominator for rational approximation; see fractions.limit_denominator
    rational_denom_limit: int   # Max denominator for Decimal to Fraction conversion. ATTN: Deprecate?
    max_denom: int              # Maximum denominator value for which rational expression is done
    exclude_denoms: set[int]    # Set of denominator values for which to suppress rational expression
    rounding: str               # How rounding is done, taken from decimal package (e.g., ROUND_HALF_UP)
    round_mask: Decimal         # Decimal value that determines the exponent of rounded values. See decimal.quantize.
    decimal_digits: int         # Current decimal precision (in digits) used for display
    nice_digits: int            # # digits used for aesthetically pleasing rounding
                                # must satisfy 0 <= nice_digits <= decimal_digits    # noqa: E116

def default_numeric_out_params() -> NumericOutParams:
    return {
        'denom_limit': 10**9,
        'rational_denom_limit': 1000000000,
        'max_denom': 50,
        'exclude_denoms': {10, 20, 25, 50, 100, 125, 250, 500, 1000},
        'rounding': ROUND_HALF_UP,
        'round_mask': Decimal('1.000000000'),
        'decimal_digits': 27,
        'nice_digits': 16,    # must satisfy 0 <= nice_digits <= decimal_digits
    }


@dataclass
class Environment:
    """Options governing interactive sessions, globally available.
    """
    ascii_only: bool = False
    dark_mode: bool = False
    is_interactive: bool = False
    command_number_in_prompt: bool = False
    console: Console = Console(highlight=True, theme=bright_theme)
    numeric_out_params: NumericOutParams = field(default_factory=default_numeric_out_params)
    frp_params: FrpParams = field(default_factory=default_frp_params)

    def on_ascii_only(self) -> None:
        "Require ASCII-only output, no rich text, unicode, or markdown."
        self.ascii_only = True

    def off_ascii_only(self) -> None:
        "Allow non-ascii and rich output"
        self.ascii_only = False

    def on_dark_mode(self) -> None:
        "Changes text color to suit dark colored terminals"
        self.dark_mode = True
        self.console.push_theme(dark_theme)

    def on_bright_mode(self) -> None:
        "Text color default suited for light colored terminals"
        self.dark_mode = False
        self.console.push_theme(bright_theme)

    def on_command_number_in_prompt(self) -> None:
        "Show current command number in the prompt instead of the title bar"
        self.command_number_in_prompt = True

    def off_command_number_in_prompt(self) -> None:
        "Show current command number in the title bar instead of the prompt"
        self.command_number_in_prompt = False

    def interactive_mode(self, ascii=None) -> None:
        "Indicate that this session is interactive. No need to turn this off."
        self.is_interactive = True
        if ascii is not None:
            self.ascii_only = ascii

    def console_str(self, rich_str) -> str:
        with self.console.capture() as capture:
            self.console.print(rich_str)
        return capture.get()

environment = Environment()
