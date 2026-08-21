"""A singleton environment for capturing global options in an interactive session.

This controls the output formats of objects that should print in nice
or rich ways in an interactive session. While this can be used at the
library level, it is primarily for interactive use and not thread safe.

"""
# pylint: disable=too-many-instance-attributes, redefined-builtin

from __future__ import annotations

import os
import sys

from collections.abc import Callable
from dataclasses     import dataclass, field
from decimal         import Decimal, ROUND_HALF_UP
from pathlib         import Path
from typing          import IO, Any, TypedDict

from platformdirs import user_config_dir
from rich.console import Console
from rich.theme   import Theme

bright_theme = Theme({
    "markdown.h2": "#4f2c1d underline",
    "markdown.h3": "#4f2c1d bold",
    "markdown.h4": "#4f2c1d italic",
    "repr.number": "#3333cc",
    "repr.number_complex": "#333366",
    "repr.bool_true": "#009933",
    "repr.bool_false": "#990033",
    "repr.str": "#330066",
    "repr.attrib_name": "#330000",
    "repr.attrib_value": "#000033",
    "markdown.item.bullet": "bold magenta",
    "markdown.item.number": "bold magenta",
    "markdown.code": "bold #5b84b1",
    "markdown.code_block": "#006747 on #cccccc",
})

dark_theme = Theme({
    "repr.number": "#cccc33",
    "repr.number_complex": "#cccc99",
    "repr.bool_true": "#ff66cc",
    "repr.bool_false": "#66ffcc",
    "repr.str": "#ccff99",
    "repr.attrib_name": "#ccffff",
    "repr.attrib_value": "#ffffcc",
    "markdown.code": "bold #006747 on white",
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

class InfoParams(TypedDict):
    pager: bool                # Use a pager to display long info docs
    pager_styles: bool | None  # Show styles (e.g., color) in the pager; None means auto-detect
    dialog: bool               # If True, use dialog interactive interface, else use completion interface

def default_info_params() -> InfoParams:
    return {
        'pager': True,
        'pager_styles': None,
        'dialog': True,
    }

def parse_pager_styles(v: Any) -> bool | None:
    """Converts a TOML value for pager_styles to bool | None.

    Accepts True, False, or the string "auto" (any case, and
    ignoring whitespace) for None.

    The auto case will attempt to detect the pager based on the
    setting of the PAGER/MANPAGER environment variables and whether
    `less` is available on the path.

    """
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() == 'auto':
        return None
    raise ValueError(f'pager_styles must be true, false, or "auto", got {v!r}')


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

    Offers several convenience methods for toggling most commonly
    changed configuration settings.

    """
    ascii_only: bool = False
    dark_mode: bool = False
    is_interactive: bool = False
    command_number_in_prompt: bool = False
    prompt_tag: str = "playground"
    prompt_sep: str = '> '
    info_params: InfoParams = field(default_factory=default_info_params)
    numeric_out_params: NumericOutParams = field(default_factory=default_numeric_out_params)
    frp_params: FrpParams = field(default_factory=default_frp_params)
    console: Console = Console(highlight=True, theme=bright_theme)

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

    def set_prompt(self, tag: str = '', sep: str = '') -> None:
        """Sets the tag and/or separator used for the playground prompt.

        Parameters
        ----------
        tag: the part of the prompt before the separator (and optional
            command number) [default: 'playground']
        sep: the separator between the tag (and optional command number)
            [default: '> ']

        Empty strings are skipped. Plain, unescaped text is expected;
        HTML-escaping for display and TOML-escaping for the config
        file are both handled automatically wherever these are used.

        """
        if tag:
            self.prompt_tag = tag
        if sep:
            self.prompt_sep = sep

    def on_info_dialog(self) -> None:
        self.info_params['dialog'] = True

    def off_info_dialog(self) -> None:
        self.info_params['dialog'] = False

    def on_info_pager(self, styles: bool | None = None) -> None:
        """Turns on the pager for info documents.

        The `styles` option determines whether colored/styled
        rendering should be assumed in pager output. True forces
        styling; False suppresses it; and None (the default)
        attempts to auto-detect the capability based on
        PAGER/MANPAGER and whether `less` is available.

        """
        self.info_params['pager'] = True
        self.info_params['pager_styles'] = styles

    def off_info_pager(self) -> None:
        self.info_params['pager'] = False

    def interactive_mode(self, ascii=None) -> None:
        "Indicate that this session is interactive. No need to turn this off."
        self.is_interactive = True
        if ascii is not None:
            self.ascii_only = ascii

    def load_config(self) -> None:
        """Finds and applies the first .frplib.toml in the standard search order.

        Silently skips if no config file is found. Prints a warning to stderr
        if a config file is found but cannot be parsed.

        """
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef]

        config_path = find_config()
        if config_path is None:
            return

        try:
            with config_path.open('rb') as f:
                config = tomllib.load(f)
        except Exception as exc:
            print(f"frplib: warning: could not parse {config_path}: {exc}", file=sys.stderr)
            return

        apply_config(self, config)

    def write_config(self, stream: IO[str] | None = None) -> None:
        """Writes the current environment settings as a .frplib.toml to stream (default stdout).

        The output is valid TOML and can be saved as .frplib.toml in any of the
        locations searched by find_config() to persist settings across sessions.

        """
        if stream is None:
            stream = sys.stdout

        num_pars = self.numeric_out_params
        frp_pars = self.frp_params
        info_pars = self.info_params

        def b(v: bool) -> str:
            return 'true' if v else 'false'

        def tri(v: bool | None) -> str:
            return '"auto"' if v is None else b(v)

        def toml_str(v: str) -> str:
            escaped = v.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'

        lines = [
            '# frplib configuration file',
            '# Recognized locations (first found is used):',
            '#   ./.frplib.toml',
            '#   ~/.frplib.toml',
            '#   <platform config dir>/frplib/frplib.toml',
            '#     Linux:   ~/.config/frplib/',
            '#     macOS:   ~/Library/Application Support/frplib/',
            '#     Windows: %APPDATA%/frplib/',
            '',
            f'ascii_only = {b(self.ascii_only)}   # Rich text in playground output suppressed (True) or on (False)',
            f'dark_mode = {b(self.dark_mode)}    # Dark mode (True) or Light mode (False)',
            f'command_number_in_prompt = {b(self.command_number_in_prompt)}  # Command number in prompt (True) or status bar (False)',
            f'prompt_tag = {toml_str(self.prompt_tag)}  # The text before the separator in the playground prompt.',
            f'prompt_sep = {toml_str(self.prompt_sep)}  # The separator text in the playground prompt.',
            '',
            '[info]',
            f'pager = {b(info_pars["pager"])}    # Pager for info documents on (True) or off (False)',
            '# Assume the pager can render formatting (True), suppress formatting in the pager (False), or',
            '# attempt to auto-detect formatting capability ("auto").',
            f'pager_styles = {tri(info_pars["pager_styles"])}',
            f'dialog = {b(info_pars["dialog"])}  # Interactive info search uses dialog (True) or completion (False)',
            '',
            '[numeric_out]',
            '# Current decimal precision (in digits) used for display.',
            f'decimal_digits = {num_pars["decimal_digits"]}',
            '# Digits used for aesthetically pleasing rounding, >= 0, <= decimal_digits.',
            f'nice_digits = {num_pars["nice_digits"]}',
            '# The maximum denominator with which a number will be printed as a fraction.',
            f'max_denom = {num_pars["max_denom"]}',
            '# Set of denominator values for which to suppress rational expression',
            f'exclude_denoms = [{", ".join(str(x) for x in sorted(num_pars["exclude_denoms"]))}]',
            f'denom_limit = {num_pars["denom_limit"]}',
            f'rational_denom_limit = {num_pars["rational_denom_limit"]}',
            '',
            '[frp]',
            '# Size threshold above which an FRPs Kind will not be automatically computed.',
            f'complexity_threshold = {frp_pars["complexity_threshold"]}',
            '# Steps threshold above which evolve will force intermediate FRPs to activate.',
            f'evolution_threshold  = {frp_pars["evolution_threshold"]}',
        ]
        print('\n'.join(lines), file=stream)

    def console_str(self, rich_str) -> str:
        """Captures and returns a rich string printed to the console."""
        with self.console.capture() as capture:
            self.console.print(rich_str)
        return capture.get()


#
# Config file loading
#

# Schema mapping TOML section names to (env attribute, {key: converter}) pairs.
# Adding a new configurable param means adding one entry here and one line in write_config.
SECTION_SCHEMA: dict[str, tuple[str, dict[str, Callable[[Any], Any]]]] = {
    'info': ('info_params', {
        'pager':        bool,
        'dialog':       bool,
        'pager_styles': parse_pager_styles,
    }),
    'numeric_out': ('numeric_out_params', {
        'decimal_digits':       int,
        'nice_digits':          int,
        'max_denom':            int,
        'denom_limit':          int,
        'rational_denom_limit': int,
        'exclude_denoms':       lambda v: set(v),
    }),
    'frp': ('frp_params', {
        'complexity_threshold': int,
        'evolution_threshold':  int,
    }),
}


def find_config() -> Path | None:
    """Return the first readable .frplib.toml found in the standard search order, or None.

    Search order (most specific first):
      1. ./.frplib.toml          — project-local override
      2. ~/.frplib.toml          — simple per-user setting (all platforms)
      3. <user_config_dir>/frplib/frplib.toml  — platform config dir
         (~/.config/frplib/ on Linux, ~/Library/Application Support/frplib/ on macOS,
          %APPDATA%/frplib/ on Windows)

    """
    home = Path.home()
    candidates = [
        Path('.frplib.toml'),
        home / '.frplib.toml',
        Path(user_config_dir('frplib')) / 'frplib.toml',
    ]
    return next((p for p in candidates if p.is_file() and os.access(p, os.R_OK)), None)


def apply_config(env: 'Environment', config: dict) -> None:
    """Applies a parsed TOML config dict to env, silently ignoring unknown keys.

    Top-level boolean keys (e.g., ascii_only, dark_mode, command_number_in_prompt) are
    applied directly. Sectioned params ([numeric_out], [frp], [info]) are applied
    via SECTION_SCHEMA, which maps each key to a converter function. If a value
    fails conversion, it is skipped with a warning printed to stderr.

    """
    if 'ascii_only' in config:
        env.ascii_only = bool(config['ascii_only'])
    if 'dark_mode' in config:
        env.on_dark_mode() if config['dark_mode'] else env.on_bright_mode()
    if 'command_number_in_prompt' in config:
        env.command_number_in_prompt = bool(config['command_number_in_prompt'])
    if 'prompt_tag' in config and isinstance(config['prompt_tag'], str) and config['prompt_tag']:
        env.prompt_tag = config['prompt_tag']
    if 'prompt_sep' in config and isinstance(config['prompt_sep'], str) and config['prompt_sep']:
        env.prompt_sep = config['prompt_sep']

    for section, section_spec in SECTION_SCHEMA.items():
        attr, converters = section_spec
        if section in config:
            target = getattr(env, attr)
            for key, convert in converters.items():
                if key in config[section]:
                    try:
                        target[key] = convert(config[section][key])
                    except Exception as exc:
                        print(f"warning: invalid value for [{section}].{key} in .frplib.toml: {exc}", file=sys.stderr)


#
# Defining the Session Environment
#

environment = Environment()
