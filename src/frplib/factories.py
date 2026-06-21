"""Decorators and wrappers for custom factory functions of several types

Factories are just functions that return an object of a specific type,
but we wrap such functions in a callable object that manages the
documentation, help, and other features in a way that is more
friendly in the repl.

These wrapper classes are not used directly, however. Rather, we
define a decorator for each type of factory and use those decorators
to mark/transform factory functions.

This module is generic in the sense that the factory creators are
parameterized by the information needed to create the specific
decorators. The concrete decorators are defined in the appropriate
modules, though the wrapper classes are defined here.

Currently, we have three types:

  + @statistic_factory
  + @kind_factory
  + @frp_factory

See statistics.py, kinds.py, and frps.py respectively for the
concrete definitions.

"""

from __future__ import annotations

import inspect

from collections.abc   import Callable
from functools         import update_wrapper, wraps

from rich.markup       import escape


#
# Helpers
#

def doc_of(f: Callable, auto_doc: str | bool = False, pars=None) -> str:
    """Returns a cleaned docstring for the given callable.

    If auto_doc is falsy, the .__doc__ attribute is cleaned for
    spacing and indentation (cf. inspect.cleandoc).

    Otherwise, the docstring is treated as a template where
    constructs like {v} where v is a parameter of the function
    are replaced by the name of the parameter. Other {} constructs
    should be escaped by doubling braces, e.g., {{v}} becomes {v}
    in the resulting string.

    """
    if not f.__doc__:
        return ''

    doc_string = inspect.cleandoc(f.__doc__)

    if not auto_doc:
        return doc_string

    par_names = {p: p for p in pars}
    return doc_string.format(**par_names)


#
# Wrapper class for all factories
#
# This is a callable class that delegates to the underlying function
# but manages representation and documentation.
#
# NOTE: This is not intended for users. They should only use
# the factory decorators.
#

class Factory:
    """Wrapper class for all sorts of factories.

    This wraps a callable and delegates all calls to that callable.
    The various parameters specify how documentation and help strings
    are constructed for the factory.

    Parameters
    ----------
    f - The factory function being wrapped. It can be any callable
        but is typically a function.

    summary - a short documentation string shown in the playground
        repl when the factory itself is printed.

    name - if supplied, an alternate name for the factory itself.
        If not supplied, the name of the wrapped function is used.
        This name is assigned to the __name__ property of the factory.

    doc - a long documentation string used to construct the help
        text for the factory. This is coded as the repr and will
        show at the beginning of help or info on the object.

    prefix - a prefix string attached to the summary and doc,
        typically describing what type of factory this is.
        This eliminates redundancy in the docstrings and allows
        easier processing of the docs for other purposes.

    auto_doc - If True, the documentation for the object produced
        by the factory (if available) will be generated from the
        docstring for the factory. In this case, the docstring
        should be a template with each factory argument in {}s.
        For the factory, the names of the variables are used,
        for the object returned, their values are used. Use {{}}s
        to get actual braces around something.  If a string,
        the string is used as the template rather than the
        given docstring. If false, no {}s are required as the
        docstrings are not templates. This only applies to
        factories that return objects with docstrings.

    allow_markup - If True, then the summary string is treated
        as a Rich text string with markup structures. If False,
        any Rich markup is escaped.

    pars - If supplied, this should be a parameter map mapping
        parameters to the callable to inspect.Parameter objects.
        This parameter exists to avoid repeated calls to
        inspect.signature.

    """
    def __init__(
            self,
            f: Callable,
            summary='',
            *,
            name: str | None = None,
            doc='',
            prefix: str | Callable | None = '',
            auto_doc: str | bool = False,
            allow_markup=False,
            pars=None
    ):
        self._fn = f
        update_wrapper(self, f)
        if name:
            self.__name__ = name
        self._allow_markup = allow_markup

        if pars and auto_doc:
            self._pars = pars
        elif auto_doc:
            self._pars = inspect.signature(f).parameters
        else:
            self._pars = None

        desc = doc or doc_of(f, auto_doc, self._pars) or summary
        if callable(prefix):
            prefix_str = prefix(desc)
        elif prefix is None:
            prefix_str = ''
        elif not prefix:
            prefix_str = self._default_prefix(desc)
        else:
            prefix_str = prefix

        self._long = prefix_str + (doc or doc_of(f, auto_doc, self._pars) or summary)
        if not summary:
            self._short = self._long.split('\n\n')[0].rstrip()
        else:
            self._short = prefix_str + summary

        self.__doc__ = self._long

    def __call__(self, *args, **kwds):
        return self._fn(*args, **kwds)

    def __repr__(self):
        return self._long

    def __frplib_repr__(self):
        return self._short if self._allow_markup else escape(self._short)

    def _default_prefix(self, s):
        if not s:
            return 'A factory'
        return 'A factory that '

class StatisticFactory(Factory):
    """Wrapper class for a statistic factory.

    This is just Factory with an appropriate default prefix.

    """
    def _default_prefix(self, s):
        if not s:
            return 'A statistic factory'
        return 'A factory producing a statistic that '

class ConditionFactory(StatisticFactory):
    """Wrapper class for a condition factory.

    This is just Factory with an appropriate default prefix.

    """
    def _default_prefix(self, s):
        if not s:
            return 'A condition factory'
        return 'A factory producing a condition that '

class KindFactory(Factory):
    """Wrapper class for a Kind factory.

    This is just Factory with an appropriate default prefix.

    """
    def _default_prefix(self, s):
        if not s:
            return 'A Kind factory'
        return 'A factory producing a Kind that represents '

class FrpFactory(Factory):
    """Wrapper class for an FRP factory.

    This is just Factory with an appropriate default prefix.

    """
    def _default_prefix(self, s):
        if not s:
            return 'An FRP factory'
        return 'A factory producing an FRP that represets '


#
# Parametric Factory Decorators
#
# These allow the construction of decorators for statistic-like and object-like (e.g., Kind, FRP)
# factory decorators parameterized by the appropriate classes and converters.
#
# Note: this depends on _stat_keys, a list of keyword arguments to the function statistic
# that the statlike factory decorators accept. These would need to change if statistic's
# interface were to change. We don't read those directly from statistic to avoid
# circular imports
#

def _make_param_map(pars):
    """Creates a function that map parameter names to values.

    pars is a dict mapping parameter names to inspect.Parameter objects
    obtained by inspect.signature.

    Returns the parameter-mapping function.

    """
    def get_values(*args, **kwds) -> dict:
        val_map = {}
        for i, p in enumerate(pars):
            # We don't check the ordering here because python will do it
            # when the function is defined. E.g., kw-only must follow positional.
            if pars[p].kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                val_map[pars[p].name] = args[i]   # Again, these must be first
            elif pars[p].kind == inspect.Parameter.VAR_POSITIONAL:
                val_map[pars[p].name] = tuple(args[i:])
            else:
                val_map[pars[p].name] = kwds[pars[p].name]
        return val_map

    return get_values

def _make_sig(name: str, pars, param_vals) -> str:
    """Returns a signature string for a function derived from a parameter map.

    name - the name of the function
    pars - a dictionary mapping parameter names to inspect.Parameter objects
    param_vals - a dictionary mapping names to actual parameter values.

    """
    sig = [name, '(',]
    for p in pars:
        if len(sig) > 2:
            sig.append(', ')

        if pars[p].kind == inspect.Parameter.POSITIONAL_ONLY:
            sig.append(str(param_vals[p]))
        elif pars[p].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if p in param_vals:
                sig.append(str(param_vals[p]))
            elif pars[p].default != inspect.Parameter.empty:
                sig.append(f'{p}={pars[p].default}')
        elif pars[p].kind == inspect.Parameter.VAR_POSITIONAL:
            sig.append(', '.join(map(str, param_vals[p])))
        else:
            break  # NOTE: We do not include keyword-only in the name
    sig.append(')')
    return ''.join(sig)

def statlike_factory(
        cast_to: type,
        cast_with: Callable,
        factory_class: type,
        valid_kwds: list[str],
        f: Callable,
        *,
        doc='',
        summary='',
        factory_name='',
        auto_doc: str | bool = False,
        auto_name: str | bool = True,
        allow_markup=False,
        **stat_kwds
):                                     # pylint: disable=too-many-locals, too-many-arguments
    """Creates a factory for a function that returns a callable with its own docstring.

    This is parameterized by the type cast_to of object the function should return,
    a conversion function cast_with that creates that object from the return value
    if it is not, and factory_class a subclass of Factory.

    The other named keyword arguments correspond to those for Factory.

    **stat_kwds are keywords for cast_with that can be passed through to
    do the conversion.

    Returns the corresponding factory.

    """
    stat_args = {k: stat_kwds[k] for k in valid_kwds if k in stat_kwds}

    if auto_doc:
        if isinstance(auto_doc, str):
            inner_doc = auto_doc
        else:
            inner_doc = doc or inspect.cleandoc(f.__doc__ or '')
    else:
        inner_doc = ''

    if auto_name:
        inner_name = auto_name if isinstance(auto_name, str) else (factory_name or f.__name__ or '')
    else:
        inner_name = ''

    if not inner_doc and not inner_name:            # pylint: disable=no-else-return
        @wraps(f)
        def stat_fact(*args, **kwds):
            stat = f(*args, **kwds)

            if isinstance(stat, cast_to):
                return stat

            return cast_with(stat, **stat_args)

        return factory_class(stat_fact, doc=doc, summary=summary, name=factory_name,
                             allow_markup=allow_markup)
    else:
        pars = inspect.signature(f).parameters
        param_map = _make_param_map(pars)

        @wraps(f)
        def stat_fact(*args, **kwds):
            stat = f(*args, **kwds)
            params = param_map(*args, **kwds)

            if not isinstance(stat, cast_to):
                stat = cast_with(stat, **stat_args)

            if inner_name:
                stat.name = _make_sig(inner_name, pars, params)
            if inner_doc:
                stat.doc = inner_doc.format(**params)
            return stat

        return factory_class(stat_fact, doc=doc, summary=summary, name=factory_name,
                             allow_markup=allow_markup, auto_doc=auto_doc, pars=pars)

def objlike_factory(
        cast_to: type,
        cast_with: Callable,
        factory_class: type,
        valid_kwds: list[str],
        f: Callable,
        *,
        summary='',
        doc='',
        name: str | None = None,
        allow_markup=False,
        **extra_kwargs
):
    """Creates a factory for a function that returns an object without its own docstring.

    This is parameterized by the type cast_to of object the function should return,
    a conversion function cast_with that creates that object from the return value
    if it is not, and factory_class a subclass of Factory.

    The other named keyword arguments correspond to those for Factory.

    **extra_kwds are keywords for cast_with that can be passed through to
    do the conversion.

    Returns the corresponding factory.

    """
    _cast_keys = {k: extra_kwargs[k] for k in valid_kwds if k in extra_kwargs}

    @wraps(f)
    def obj_fact(*args, **kwds):
        obj = f(*args, **kwds)

        if not isinstance(obj, cast_to):
            return cast_with(obj, **_cast_keys)
        return obj

    return factory_class(obj_fact, summary=summary, doc=doc,
                         name=name, allow_markup=allow_markup)
