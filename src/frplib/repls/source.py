"""Displays the source code of a function or wrapped object, syntax-highlighted."""

from __future__ import annotations

import inspect

from rich.syntax import Syntax

from frplib.env           import environment
from frplib.repls.paging  import print_paged
from frplib.statistics    import Statistic

__all__ = ['source']


def _resolve_source_target(f):
    """Attempts to resolve the underlying source-bearing object backing `f`.

    This correctly handles various frplib wrapped objects:

    1. Factory-wrapped callables
    2. ConditionalKind's and ConditionalFRP's defined from functions
    3. Statistics

    Objects that set __wrapped__ via functools.wraps/update_wrapper
    will work with source as well.

    Note that at the moment neither ConditionalKind/ConditionalFRP
    nor Statistic set __wrapped__ but instead store the original
    function separately. This might change in a future version.

    """
    target = inspect.unwrap(f)
    if getattr(target, '_original_fn', None) is not None:
        # Conditional Kinds and Conditional FRPs built from functions
        target = target._original_fn     # pylint: disable=protected-access
    elif isinstance(target, Statistic):
        target = target.fn

    return target


def source(f) -> None:
    """Displays the source code of `f`, syntax-highlighted, in the playground.

    This works for plain functions, and for frplib's wrapped objects,
    which includes factories (uniform, constant, shuffle, etc.),
    conditional Kinds/FRPs built from a function, and Statistics.

    Notee: A conditional Kind/FRP built from a dict has no separate
    source to show and reports that cleanly.

    """
    target = _resolve_source_target(f)
    try:
        code = inspect.getsource(target)
    except (OSError, TypeError) as e:
        label = repr(f)
        if hasattr(f, '__name__') or hasattr(f, 'name'):
            label = getattr(f, '__name__', '') or getattr(f, 'name', '')
        environment.console.print(f'No source available for {label}: {e}')
        return

    code_theme = 'monokai' if environment.dark_mode else 'slate'
    print_paged(Syntax(code, 'python', theme=code_theme, line_numbers=True, word_wrap=True))
