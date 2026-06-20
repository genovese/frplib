"""Decorators and wrappers for custom factory functions of several types"""

from __future__ import annotations

import inspect

from collections.abc   import Callable
from functools         import update_wrapper, wraps

from rich.markup       import escape

from frplib.exceptions import FactoryError
from frplib.frps       import frp, is_frp
from frplib.kinds      import is_kind, kind
from frplib.statistics import Condition, Statistic, condition, statistic


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
# Statistic Factories and their User-Facing Decorators
#

_stat_keys = ['name', 'codim', 'dim', 'description', 'monoidal', 'strict', 'arg_convert']

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
    stat_args = {k: stat_kwds[k] for k in _stat_keys if k in stat_kwds}

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
    if f is None:
        def decorator(fn: Callable):
            return statistic_factory(fn, summary=summary, doc=doc, factory_name=factory_name,
                                     auto_doc=auto_doc, auto_name=auto_name,
                                     allow_markup=allow_markup, **stat_kwds)
        return decorator

    return _statlike_factory(Statistic, statistic, StatisticFactory,
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
    if f is None:
        def decorator(fn: Callable):
            return condition_factory(fn, summary=summary, doc=doc, factory_name=factory_name,
                                     auto_doc=auto_doc, auto_name=auto_name,
                                     allow_markup=allow_markup, **stat_kwds)
        return decorator

    return _statlike_factory(Condition, condition, ConditionFactory,
                             f, doc=doc, summary=summary, factory_name=factory_name,
                             auto_doc=auto_doc, auto_name=auto_name,
                             allow_markup=allow_markup, **stat_kwds)

#
# def statistic_factory(
#         f=None,
#         *,
#         doc='',
#         summary='',
#         name='',
#         auto_doc: str | bool = False,
#         auto_name: str | bool = True,
#         allow_markup=False,
#         **stat_kwds
# ):
#     """ATTN"""
#     stat_args = {k: stat_kwds[k] for k in _stat_keys if k in stat_kwds}
#
#     if f is None:
#         def decorator(fn: Callable):
#             return statistic_factory(fn, summary=summary, doc=doc, name=name,
#                                      auto_doc=auto_doc, auto_name=auto_name,
#                                      allow_markup=allow_markup, **stat_kwds)
#         return decorator
#
#     if auto_doc:
#         if isinstance(auto_doc, str):
#             inner_doc = auto_doc
#         else:
#             inner_doc = doc or inspect.cleandoc(f.__doc__) or ''
#     else:
#         inner_doc = ''
#
#     if auto_name:
#         inner_name = auto_name if isinstance(auto_name, str) else (name or f.__name__ or '')
#     else:
#         inner_name = ''
#
#     if not inner_doc and not inner_name:            # pylint: disable=no-else-return
#         @wraps(f)
#         def stat_fact(*args, **kwds):
#             stat = f(*args, **kwds)
#
#             if isinstance(stat, Statistic):
#                 return stat
#
#             return statistic(stat, **stat_args)
#
#         return Factory(stat_fact, doc=doc, summary=summary, name=name,
#                        prefix='A factory producing a statistic that ', allow_markup=allow_markup)
#     else:
#         pars = inspect.signature(f).parameters
#         param_map = _make_param_map(pars)
#
#         @wraps(f)
#         def stat_fact(*args, **kwds):
#             stat = f(*args, **kwds)
#             params = param_map(*args, **kwds)
#
#             if not isinstance(stat, Statistic):
#                 stat = statistic(stat, **stat_args)
#
#             if inner_name:
#                 stat.name = _make_sig(inner_name, pars, params)
#             if inner_doc:
#                 stat.doc = inner_doc.format(**params)
#             return stat
#
#         return Factory(stat_fact, doc=doc, summary=summary, name=name,
#                        prefix='A factory producing a statistic that ', allow_markup=allow_markup,
#                        auto_doc=auto_doc, pars=pars)
#


#
# Kind Factory Decorator
#

def kind_factory(
        f=None,
        *,
        summary='',
        doc='',
        display=None,  # TODO: ATTN for Kind.Display enum later
        name: str | None = None,
        allow_markup=False,
):
    """ATTN"""
    if f is None:
        def decorator(fn: Callable):
            return kind_factory(fn, display=display, summary=summary, doc=doc,
                                name=name, allow_markup=allow_markup)
        return decorator

    @wraps(f)
    def kind_fact(*args, **kwds):
        k = f(*args, **kwds)

        if not is_kind(k):
            return kind(k)  # TODO: ATTN kind(f, display=display) when display implemented
        return k

    return KindFactory(kind_fact, summary=summary, doc=doc,
                       name=name, allow_markup=allow_markup)


#
# FRP Factory Decorator
#

def frp_factory(
        f,
        *,
        summary='',
        doc='',
        name: str | None = None,
        allow_markup=False,
):
    """ATTN"""
    if f is None:
        def decorator(fn: Callable):
            return frp_factory(fn, summary=summary, doc=doc,
                               name=name, allow_markup=allow_markup)
        return decorator

    @wraps(f)
    def frp_fact(*args, **kwds):
        x = f(*args, **kwds)

        if not is_frp(x):
            return frp(x)
        return x

    return FrpFactory(frp_fact, summary=summary, doc=doc,
                      name=name, allow_markup=allow_markup)
