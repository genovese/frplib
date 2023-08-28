#
# A singleton environment for capturing global options in an interactive session.
#
# This controls the output formats of objects that should print in nice
# or rich ways in an interactive session. While this can be used at the
# library level, it is primarily for interactive use and not thread safe.
#
from __future__ import annotations

from dataclasses  import dataclass

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
})


@dataclass
class Environment:
    """Options governing interactive sessions, globally available.
    """
    ascii_only: bool = False
    is_interactive: bool = False
    console: Console = Console(highlight=True, theme=bright_theme)  # ATTN: auto-detect dark?

    def on_ascii_only(self) -> None:
        "Require ASCII-only output, no rich text, unicode, or markdown."
        self.ascii_only = True

    def off_ascii_only(self) -> None:
        "Allow non-ascii and rich output"
        self.ascii_only = False

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
