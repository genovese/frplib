"""Decorators and wrappers for custom factory functions of several types"""

from __future__ import annotations

import inspect

from collections.abc   import Callable
from functools         import update_wrapper, wraps

from rich.markup       import escape

from frplib.exceptions import FactoryError


__all__ = [
    'FactoryError',
    'statistic_factory',
    'condition_factory',
    'kind_factory',
    'frp_factory',
]


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


# TODO: Fill in proper docstrings for the factory classes and decorators

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
    """Wrapper class for all sorts of factories."""
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
    """Wrapper class for a statistic factory."""
    def _default_prefix(self, s):
        if not s:
            return 'A statistic factory'
        return 'A factory producing a statistic that '

class ConditionFactory(StatisticFactory):
    """Wrapper class for a condition factory."""
    def _default_prefix(self, s):
        if not s:
            return 'A condition factory'
        return 'A factory producing a condition that '

class KindFactory(Factory):
    """Wrapper class for a Kind factory."""
    def _default_prefix(self, s):
        if not s:
            return 'A Kind factory'
        return 'A factory producing a Kind that represents '

class FrpFactory(Factory):
    """Wrapper class for an FRP factory."""
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

def _statlike_factory(
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
):                                     # pylint: disable=too-many-locals
    """ATTN"""
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

def _objlike_factory(
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
    """ATTN"""
    _cast_keys = {k: extra_kwargs[k] for k in valid_kwds if k in extra_kwargs}

    @wraps(f)
    def obj_fact(*args, **kwds):
        obj = f(*args, **kwds)

        if not isinstance(obj, cast_to):
            return cast_with(obj, **_cast_keys)
        return obj

    return factory_class(obj_fact, summary=summary, doc=doc,
                         name=name, allow_markup=allow_markup)


#
# Statistic Factory Decorators (Statistic and Condition)
#

_STAT_KEYS = ['name', 'codim', 'dim', 'description', 'monoidal', 'strict', 'arg_convert']

def statistic_factory(
        f=None,
        *,
        doc='',
        summary='',
        factory_name='',
        auto_doc: str | bool = False,
        auto_name: str | bool = True,
        allow_markup=False,
        **stat_kwds
):
    """ATTN"""
    from frplib.statistics import Statistic, statistic  # TODO: avoid circularity; consider move to statistics.py

    if f is None:
        def decorator(fn: Callable):
            return statistic_factory(fn, summary=summary, doc=doc, factory_name=factory_name,
                                     auto_doc=auto_doc, auto_name=auto_name,
                                     allow_markup=allow_markup, **stat_kwds)
        return decorator

    return _statlike_factory(Statistic, statistic, StatisticFactory, _STAT_KEYS,
                             f, doc=doc, summary=summary, factory_name=factory_name,
                             auto_doc=auto_doc, auto_name=auto_name,
                             allow_markup=allow_markup, **stat_kwds)

def condition_factory(
        f=None,
        *,
        doc='',
        summary='',
        factory_name='',
        auto_doc: str | bool = False,
        auto_name: str | bool = True,
        allow_markup=False,
        **stat_kwds
):
    """ATTN"""
    from frplib.statistics import Condition, condition    # TODO: avoid circularity; consider moving to statistics.py

    if f is None:
        def decorator(fn: Callable):
            return condition_factory(fn, summary=summary, doc=doc, factory_name=factory_name,
                                     auto_doc=auto_doc, auto_name=auto_name,
                                     allow_markup=allow_markup, **stat_kwds)
        return decorator

    return _statlike_factory(Condition, condition, ConditionFactory, _STAT_KEYS,
                             f, doc=doc, summary=summary, factory_name=factory_name,
                             auto_doc=auto_doc, auto_name=auto_name,
                             allow_markup=allow_markup, **stat_kwds)


#
# Kind Factory Decorator
#

def kind_factory(
        f=None,
        *,
        summary='',
        doc='',
        display=None,  # TODO: ATTN for Kind.Display enum later when it is implemented
        name: str | None = None,
        allow_markup=False,
):
    """ATTN"""
    from frplib.kinds      import Kind, kind    # TODO: lazy imports avoid circularity; consider moving to kinds.py

    if f is None:
        def decorator(fn: Callable):
            return kind_factory(fn, display=display, summary=summary, doc=doc,
                                name=name, allow_markup=allow_markup)
        return decorator

    return _objlike_factory(Kind, kind, KindFactory, ['display'], f,
                            summary=summary, doc=doc, name=name, allow_markup=allow_markup, display=display)


#
# FRP Factory Decorator
#

def frp_factory(
        f=None,
        *,
        summary='',
        doc='',
        name: str | None = None,
        allow_markup=False,
):
    """ATTN"""
    from frplib.frps       import FRP, frp     # TODO: lazy imports avoid circularity; consider moving to frps.py

    if f is None:
        def decorator(fn: Callable):
            return frp_factory(fn, summary=summary, doc=doc,
                               name=name, allow_markup=allow_markup)
        return decorator

    return _objlike_factory(FRP, frp, FrpFactory, [], f,
                            summary=summary, doc=doc, name=name, allow_markup=allow_markup)
