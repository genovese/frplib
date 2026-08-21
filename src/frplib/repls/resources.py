"""Functions for opening (or copying) frplib's bundled PDF resources.

Covers the Cookbook, Cheatsheet, and textbook, each shipped as a PDF
under frplib.data and made available in the playground as cookbook(),
cheatsheet(), and textbook().

"""

from __future__ import annotations

import shutil

from importlib.resources import as_file, files
from pathlib             import Path

import click

from frplib.exceptions   import PlaygroundError


__all__ = ['cookbook', 'cheatsheet', 'textbook']


_RESOURCES = {
    'cookbook':   'frplib-cookbook.pdf',
    'cheatsheet': 'frplib-cheatsheet.pdf',
    'textbook':   'probex.pdf',
}


def _open_resource(name: str, to: str | Path | None = None) -> None:
    """Opens the packaged PDF resource registered under `name` in the default viewer.

    If `to` is given, the PDF is instead copied into the named directory.
    The directory and its parents are created if they do not exist.

    """
    if name not in _RESOURCES:
        raise PlaygroundError(f'Unrecognized resource {name} cannot be opened.')

    resource = files('frplib.data') / _RESOURCES[name]
    with as_file(resource) as path:
        if to is None:
            click.launch(str(path))
        else:
            dest_dir = Path(to)
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest_dir / path.name)

def cookbook(to: str | Path | None = None) -> None:
    """Opens the frplib Cookbook (PDF) in your default viewer.

    If `to` is given, a directory path, copies the PDF there instead
    of opening it.

    """
    _open_resource('cookbook', to)

def cheatsheet(to: str | Path | None = None) -> None:
    """Opens the frplib Cheatsheet (PDF) in your default viewer.

    If `to` is given, a directory path, copies the PDF there instead
    of opening it.

    """
    _open_resource('cheatsheet', to)

def textbook(to: str | Path | None = None) -> None:
    """Opens the textbook Probability Explained in your default viewer.

    If `to` is given, a directory path, copies the PDF there instead
    of opening it.

    This works with the version of the book currently bundled with
    frplib. If the book is being updated frequently, as in a course,
    you might prefer to obtain the book from another source.

    """
    _open_resource('textbook', to)
