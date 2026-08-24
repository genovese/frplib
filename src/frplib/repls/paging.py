"""Shared pager configuration and paged-printing helpers for the playground repl.

Used by both info.py (for info documents) and help.py (for custom and
builtin help), so a single `less -F -R` auto-detection and override
policy governs paging everywhere in the playground.

"""

from __future__ import annotations

import contextlib
import os
import shutil

from collections.abc import Callable
from typing           import Any

from frplib.env import environment

__all__ = ['configured_pager', 'pager_styles', 'print_paged', 'paged_help']


def _autodetect_pager_styles() -> bool:
    """Returns True if we can reasonably expect ANSI colors to render through the pager.

    If the user has set PAGER or MANPAGER themselves, we trust their choice
    outright. Otherwise, this is True only when `less` is available, since
    it is the only pager we explicitly configure with color support;
    see configured_pager.

    """
    if os.environ.get('PAGER') or os.environ.get('MANPAGER'):
        return True
    return shutil.which('less') is not None

@contextlib.contextmanager
def configured_pager():
    """Context manager that temporarily configures a well-behaved PAGER, if possible.

    If the user has not set PAGER or MANPAGER themselves, and `less` is
    available on PATH (see _autodetect_pager_styles), this *temporarily*
    sets the PAGER environment variable to invoke `less` with the -F -R
    options. (The skip the pager for text under one screen and render
    ANSI colors properly.) The environment variable is restored on exit
    from the context.

    Otherwise, this is a no-op. Note that a pager the user has explicitly
    selected is never overridden. Because this only touches the PAGER
    environment variable, it benefits any code that pages independently
    of the frplib console, such as Python's builtin `help`; see paged_help.

    """
    if os.environ.get('PAGER') or os.environ.get('MANPAGER') or not shutil.which('less'):
        yield
        return

    prior = os.environ.get('PAGER')
    os.environ['PAGER'] = 'less -F -R'
    try:
        yield
    finally:
        if prior is None:
            os.environ.pop('PAGER', None)
        else:
            os.environ['PAGER'] = prior

def pager_styles() -> bool:
    """Returns whether styles (e.g., color) should be shown in the environment console's pager.

    Uses environment.info_params['pager_styles'] if it has been set to
    True or False explicitly (see Environment.on_info_pager); otherwise
    auto-detects via _autodetect_pager_styles.

    """
    styles = environment.info_params.get('pager_styles')
    if styles is None:
        styles = _autodetect_pager_styles()
    return styles

def print_paged(renderable: Any, *, pager: bool | None = None) -> None:
    """Prints `renderable` on the environment console, through a pager if enabled.

    If `pager` is not given, environment.info_params['pager'] governs
    whether a pager is used at all. When paging, pager_styles() governs
    whether styles are shown.

    """
    if pager is None:
        pager = environment.info_params.get('pager', False)

    if not pager:
        environment.console.print(renderable)
        return

    with configured_pager(), environment.console.pager(styles=pager_styles()):
        environment.console.print(renderable)

def paged_help(builtin_help: Callable, *args) -> None:
    """Calls `builtin_help(*args)` with PAGER configured the same way as print_paged.

    Python's builtin `help` manages its own pager invocation internally
    (via pydoc), so frplib cannot page its output directly through the
    environment console. Instead, this configures PAGER the same way
    print_paged does -- when environment.info_params['pager'] is enabled
    -- so pydoc's own pager invocation benefits from the same `less -F -R`
    auto-detection, without frplib needing to know anything about pydoc's
    internals.

    """
    if environment.info_params.get('pager', False):
        with configured_pager():
            builtin_help(*args)
    else:
        builtin_help(*args)
