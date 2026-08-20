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


def help(obj=None, builtin=False, *, invoked_by=None) -> None:    # pylint: disable=redefined-builtin
    """Specialized version of Python built-in help for the frplib playground.

    This handles some types of objects specially, including those with
    a '__frplib_help__' attribute, and otherwise delegates to the built-in
    help.

    If object has an __frplib_help__ attribute, this determines the output.
    This can be:
        + a method of the object that returns a renderable object (a string
          or a rich.console.RenderableType), which is called with the
        value of the `invoked_by` argument and its return value rendered.
        If the method returns None, builtin help is used as a fallback.

        + a string, which is assumed to be markdown formatted and
          rendered as such, or

        + a renderable object, which is rendered directly

    Without an __frplib_help__ attribute, classes, modules,
    routines, and properties are automatically delegated to the
    built-in help.

    If the object has a __doc__ attribute, a clean version of that attribute
    is printed.

    Otherwise, this delegates to te the built-in help.

    Parameters
    ----------
    obj: If supplied, an object to get help on. If not, this invokes
        the builtin help with no arguments.

    builtin: If True, delegate to builtin help immediately. (Default: False)

    invoked_by: a value passed to __frplib_help__ when it is a method.
        This allows the method to track where it is coming from and
        react accordingly. The key use case is when the method looks
        up an info file for an object which does not exist. In the
        info() display this will lead to help(obj) being called
        which would look for the info data pointlessly (as it is
        not there). So by setting invoked_by='info', this method
        can bail to the builtin help immediately (by returning None).

    """
    if obj is None:
        _builtin_help()
    elif builtin:
        _builtin_help(obj)
    elif hasattr(obj, '__frplib_help__'):
        fh = obj.__frplib_help__
        if callable(fh):
            help_doc = fh()
            if help_doc is not None:
                environment.console.print(fh(invoked_by))
            else:
                _builtin_help(obj)
        elif isinstance(fh, str):
            environment.console.print(Markdown(fh))
        else:
            environment.console.print(fh)
    elif (inspect.isroutine(obj)
          or inspect.ismodule(obj)
          or isinstance(obj, (type, property))):
        _builtin_help(obj)
    elif getattr(obj, '__doc__', None):  # ATTN:Aug2026 Not sure if this branch is a good idea
        environment.console.print(inspect.cleandoc(obj.__doc__))
    else:
        _builtin_help(obj)

# ATTN:Aug2026 The following are provisional and experimental
# Considering how users can annotate objects to make notes
# Best if this could be serialized with the objects
# Not sure if worth it. This version just replaces the __doc__
# for help on that object.

def annotate(obj, doc: str, drop_frplib_help=False) -> None:
    """Annotates an instance of an object with a specified docstring.

    This updates the instance-specific __doc__ attribute of the object
    with the given string. This will show up in the frp playground
    as the help string.

    If it does not, the object might have a special __frplib_help__
    attribute set. The `drop_frplib_help` argument, if set to True,
    will eliminate this special attribute for this instance only,
    making the annotation show up as the help text for the object.

    Alternatively, you can use the `view_annotation` function to see
    in the playground any instance specific annotations you have
    added to an object.

    """
    setattr(obj, '__doc__', doc)
    if drop_frplib_help:
        delattr(obj, '__frplib_help__')

def view_annotation(obj) -> None:
    """Displays the object's __doc__ attribute nicely in the playground."""
    environment.console.print(inspect.cleandoc(obj.__doc__))
