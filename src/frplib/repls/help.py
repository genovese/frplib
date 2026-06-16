"""Custom help function for the frplib playground repl.

Specially handles frplib objects, either with Markdown
documentation or just their __doc__ properties.
Prints the help in a clean way.

Otherwise, delegates to the Python builtin help.

Classes, modules, routines (methods, functions, wrappers, etc),
and properties are automatically delegated to the built-in help.

Objects with a __frplib_help__ attribute use that attribute to
generate the help text. If it is a method of the object, it is
called with no arguments and should return a renderable object
(rich.console.RenderableType -- which includes Panel, Table,
Markdown, Group -- or a string). If it is a string, it is assumed to
be a markdown formatted string and is output to the console
accordingly. If it is another renderable type, it is printed
directly.

Other objects with a __doc__ attribute have a cleaned version
of that attribute printed to the console.

"""

from __future__    import annotations

import builtins
import inspect

from rich.markdown import Markdown

from frplib.env    import environment


_builtin_help = builtins.help

def help(obj=None):    # pylint: disable=redefined-builtin
    """Specialized version of Python built-in help for the frplib playground.

    This handles some types of objects specially, including those with
    a '__frplib_help__' attribute, and otherwise delegates to the built-in
    help.

    Classes, modules, routines, and properties are automatically delegated
    to the built-in help.

    If object has an __frplib_help__ attribute, this determines the output.
    This can be:

    + a method of the object that returns a renderable object (a string
      or a rich.console.RenderableType), which is called with no arguments
      and its return value rendered

    + a string, which is assumed to be markdown formatted and
      rendered as such, or

    + a renderable object, which is rendered directly

    If the object has a __doc__ attribute, a clean version of that attribute
    is printed.

    Otherwise, built-in help is used.

    """
    if obj is None:
        _builtin_help()
    elif (isinstance(obj, (type, property))
          or inspect.ismodule(obj)
          or inspect.isroutine(obj)):
        _builtin_help(obj)
    elif hasattr(obj, '__frplib_help__'):
        fh = obj.__frplib_help__
        if callable(fh):
            environment.console.print(fh())
        elif isinstance(fh, str):
            environment.console.print(Markdown(fh))
        else:
            environment.console.print(fh)
    elif getattr(obj, '__doc__', None):
        print(inspect.cleandoc(obj.__doc__))
    else:
        _builtin_help(obj)
