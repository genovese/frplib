"""Rendering and display helpers for making plots.

The plotting facility is an extra item during frplib
installation which depends on matplotlib and uses the
Agg backend and click.launch to display png files.
This is primarily intended for use in the playground,
but it can be used in code or scripts as well.
The plotting facility is obtained by specifying a
an extra feature during installation:

   `pipx install "frplib[plots]"`

for the frp application and optionally

   `pip install frplib[plots]`

within a venv. Note the ""s in the former command;
they protect the bare []s from being
interpreted by command interpreters like zsh.

The interaction between the ptpython event loop and
the matplotlib facilities and the dependence of the
latter on having a rendering backend like tkinter
makes this approach desirable.

The `get_pyplot` function forces the backend to Agg
and should be called in lieu of importing matplotlib.pylplot
directly. The user can use the ordinary matplotlib
methods by skipping this call, but be warned that
interaction with the playground's event loop can be
unpredictable or inconvenient.  The alternative
makes sense in scripts or programs that use frplib,
however.

The `show_figure` function is used to save figures
to a png file and view them with the system's
viewer.

Matplotlib is imported lazily here, so that importing
this module -- or frplib in general -- will not require
that matplotlib be installed. Only calling these
plotting functions requires that.

"""

from __future__ import annotations

import os
import tempfile

from pathlib import Path
from typing  import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from types             import ModuleType

__all__ = ['get_pyplot', 'show_figure']

_MISSING_PLOTS_MSG = (
    "Plotting requires the optional 'plots' extra."
    " Install it with `pip install frplib[plots]` in a venv"
    " or `pipx install \"frplib[plots]\"` for the frp app."
    " (Note the quotes in the latter.)"
)


def get_pyplot() -> 'ModuleType':
    """Returns matplotlib.pyplot, configured to use the Agg backend.

    This should be called before creating any figure in frplib,
    instead of directly importing matplotlib.pyplot, because this
    configures the Agg backend before pyplot's default backend
    is locked in. Agg requires no GUI tookit and is consistent
    across platforms. It is also well suited to the playground
    because it will not interact with its event loop, unlike
    the default backend.

    Raises an ImportError if matplotlib is not installed.

    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError(_MISSING_PLOTS_MSG) from e
    return plt

def view_file(fpath) -> None:
    """Opens a file (specified by `fpath`) with the system's default viewer.

    NOTE: click.launch() delegates asynchronously to the system's
    default viewer and returns immediately. So, we cannot safely
    delete the temporary file afterwards to avoid a race condition.
    We leave this for the system's ordinary temp file cleanup. (This
    is the same tradeoff that arises with as_file() in
    resources.py.)

    """
    click.launch(fpath)

def show_figure(fig: 'Figure', *, to: str | Path | None = None) -> None:
    """Displays a matplotlib Figure as a PNG, or saves it to `to`, if supplied.

    If `to` is not supplied, the figure is saved to a temporary file
    and opened with the system's default viewer.

    If `to` is supplied, it should be a file path, as either a string
    or a pathlib path. The PNG is written to that path, and no figure
    is diplayed.

    In either case, the figure is closed (in the pyplot sense)
    afterwards to avoid accumulating open figures over an extended
    playground session.

    The basic usage of this looks like:

      plt = get_pyplot()       # called before generating any figures
      fig, ax = plt.subplots()
      ax.plot(...)             # scatter, bar, or whatever
      show_figure(fig)

    """
    plt = get_pyplot()
    try:
        if to is not None:
            dest = Path(to)
            dest.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(dest)
        else:
            fd, path = tempfile.mkstemp(prefix='frplib_plot_', suffix='.png')
            os.close(fd)
            fig.savefig(path)
            view_file(path)
    finally:
        plt.close(fig)
