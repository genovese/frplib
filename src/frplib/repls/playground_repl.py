from __future__ import annotations

import ast
import linecache
import sys
import traceback as tb_module

from importlib                     import import_module
from importlib.resources           import files

# from prompt_toolkit.filters        import has_focus
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts      import print_formatted_text
from ptpython.repl                 import PythonRepl
from ptpython.python_input         import PythonInput
from rich.markdown                 import Markdown

from frplib.env        import environment
from frplib.exceptions import FrplibException
from frplib.protocols  import Renderable
from frplib.vec_tuples import VecTuple


#
# Help System
#

def info(obj_or_topic='topics', pager=False) -> None:
    """Accesses and displays help on a variety of playground topics.

    """
    def no_help():
        print_formatted_text(HTML('<violet>I could not find any guidance on that topic. '
                                  'Try info() for a list of starting points.</violet>'))

    topic = []
    if not isinstance(obj_or_topic, str):
        if hasattr(obj_or_topic, '__info__'):
            topic = obj_or_topic.__info__.split('::')
        else:
            help(obj_or_topic)
            return
    else:
        # Look for main level topic or search below
        topic = obj_or_topic.split('::')

    if topic:
        top_level = files('frplib.data') / 'playground-help'

        topic_path = top_level
        found = True
        for dir in topic[:-1]:
            topic_path = topic_path / dir
            if not topic_path.is_dir():  # Will fail if does not exist also
                found = False
                break
        if found:
            topic_path = topic_path / f'{topic[-1]}.md'
            if not topic_path.is_file():
                found = False
            else:
                help_text = topic_path.read_text()
                # Rich behaving oddly here
                code_theme = 'monokai' if environment.dark_mode else 'slate'
                info_text = Markdown(help_text, code_theme=code_theme)
                if pager:
                    with environment.console.pager():
                        environment.console.print(info_text)
                else:
                    environment.console.print(info_text)
        if not found:
            pass  # Search for topic in manifest
            no_help()  # Do this if search comes up empty
    else:
        no_help()


#
# Import Environment
#

playground_imports: dict[str, list[str]] = {
    # When there are submodules loaded, order from parent down
    # Note that symbols and module names cannot be the same
    # as we are adding both to globals()
    # ATTN: Consider *not* adding the module names to globals
    'kinds': [
        'Kind', 'ConditionalKind',
        'kind', 'conditional_kind',
        'is_kind', 'unfold', 'clean', 'fast_mixture_pow', 'bayes',
        'constant', 'uniform', 'either', 'binary',
        'symmetric', 'linear', 'geometric',
        'weighted_by', 'weighted_as', 'weighted_pairs',
        'arbitrary', 'integers', 'evenly_spaced', 'bin',
        'without_replacement', 'ordered_samples', 'subsets', 'permutations_of',
    ],
    'statistics': [
        'Statistic', 'Condition', 'MonoidalStatistic',
        'is_statistic', 'statistic', 'condition', 'scalar_statistic',
        'tuple_safe', 'infinity', 'is_true', 'is_false',
        'Chain', 'Compose', 'scalar_fn',
        'Id', 'Scalar', '__', 'Proj', '_x_',
        'Sum', 'Product', 'Count', 'Max', 'Min', 'Abs', 'SumSq',
        'Sqrt', 'Floor', 'Ceil', 'NormalCDF', 'Binomial',
        'Exp', 'Log', 'Log2', 'Log10',
        'Sin', 'Cos', 'Tan', 'ACos', 'ASin', 'ATan2', 'Sinh', 'Cosh', 'Tanh',
        'Pi', 'FromDegrees', 'FromRadians',
        'Mean', 'StdDev', 'Variance',
        'Median', 'Quartiles', 'IQR',
        'SumSq', 'Norm', 'Dot',
        'ArgMin', 'ArgMax', 'Ascending', 'Descending', 'Distinct',
        'Diff', 'Diffs', 'Permute', 'ElementOf',
        'Constantly', 'Fork', 'MFork', 'ForEach', 'IfThenElse',
        'And', 'Or', 'Not', 'Xor', 'top', 'bottom',
        'All', 'Any', 'Cases', 'Bag', 'Append', 'Prepend',
        'Get', 'Keep', 'MaybeMap',
        'Freqs', 'IndexOf', 'Contains',
    ],
    'expectations': ['E', 'Var', 'D_'],
    'frps': [
        'FRP', 'frp', 'conditional_frp', 'is_frp', 'evolve',
        'average_conditional_entropy', 'mutual_information', 'shuffle',
    ],
    'calculate': ['substitute', 'substitute_with', 'substitution'],
    'numeric': ['numeric_exp', 'numeric_ln', 'numeric_log10', 'numeric_log2',
                'numeric_abs', 'numeric_sqrt', 'numeric_floor', 'numeric_ceil',
                'nothing'],
    'quantity': ['as_quantity', 'qvec'],
    'symbolic': ['gen_symbol', 'is_symbolic', 'is_zero', 'symbol', 'symbols'],
    'utils': [
        'clone', 'compose', 'const', 'every', 'frequencies',
        'identity', 'index_of', 'index_where', 'irange', 'iterate', 'iterates',
        'lmap', 'fold', 'fold1',
        'values', 'dim', 'codim', 'size', 'typeof', 'show', 'some',
    ],
    'vec_tuples': [
        'VecTuple',
        'as_numeric_vec', 'as_scalar', 'as_vec_tuple', 'as_float', 'as_bool',
        'is_vec_tuple', 'vec_tuple', 'join',
    ],
    'market': [
        'Market',
    ],
    'extras': [
        'components',
    ],
}

# ATTN: maybe don't load the modules into globals?

def import_playground(globals) -> None:
    modules = playground_imports.keys()
    for module_name in modules:
        module = import_module(f'frplib.{module_name}')
        globals[module_name] = module
        for symbol_name in playground_imports[module_name]:
            globals[symbol_name] = getattr(module, symbol_name)
    d = import_module('decimal')
    globals['decimal'] = d
    globals['Decimal'] = getattr(d, 'Decimal')

def remove_playground(globals) -> None:
    modules = playground_imports.keys()
    for module_name in modules:
        for symbol_name in playground_imports[module_name]:
            if symbol_name in globals:
                del globals[symbol_name]
        if module_name in globals:
            del globals[module_name]


#
# Helpers for handling IndexErrors
#
# As this is a commonly occurring interactive error, we want to
# give helpful error messages without obscure stack frames in
# simple cases and meaningful stack frames otherwise.
#
# For example, with
#
# > v = vec_tuple(1, 2, 3)
# > v[4]
#
# we want a simple message identifying the type and index, without
# a traceback referencing __getitem__.
#
# However, with a call to a user-defined function like foo(v), we
# need more detail. Here, we distinguish two cases: 1. a function
# defined in the repl as a multiline input and 2. a function defined
# in an extern file. In case 1, we give a stack trace that is trimmed
# to focus on the lines of code in the input. In case 2, we give
# a simple error message with a function `explain_error` that gives
# the full traceback.
#
# We also put the last exception in the variable _e for the user.
#

def _describe_container(obj) -> str:
    """Gives a human-readable description of a subscriptable object for error messages."""
    if isinstance(obj, VecTuple):
        return f'a VecTuple of dimension {len(obj)}'
    if isinstance(obj, dict):
        return f'a {type(obj).__name__} of {len(obj)} entries'
    if isinstance(obj, (list, tuple)):
        return f'a {type(obj).__name__} of length {len(obj)}'
    if isinstance(obj, str):
        return f'a string of length {len(obj)}'
    try:
        return f'a {type(obj).__name__} of length {len(obj)}'
    except TypeError:
        return f'a {type(obj).__name__}'

def _subscript_error_context(tb, s1_format) -> str | None:
    """Shared context extraction for IndexError and KeyError tracebacks.

    Strategy 1: look for a Python __getitem__ frame and read self/key directly.
    This works for frplib types (e.g. VecTuple) that have a Python-level
    __getitem__. The message is produced by s1_format(obj, key).

    Strategy 2: read the source line directly from linecache for the innermost
    playground frame and parse it with the AST to find the subscripted name.
    This works for built-in types (list, tuple, str, dict) whose __getitem__
    is in C and therefore has no Python frame.
    """
    summaries = tb_module.extract_tb(tb)
    live = list(tb_module.walk_tb(tb))

    # Strategy 1: Python-level __getitem__ frame
    for frame, _lineno in live:
        if frame.f_code.co_name == '__getitem__':
            obj = frame.f_locals.get('self')
            key = frame.f_locals.get('key')
            if obj is not None:
                return s1_format(obj, key)

    # Strategy 2: source line from playground frame via linecache
    for (frame, _lineno), summary in reversed(list(zip(live, summaries))):
        if not _is_playground_file(summary.filename):
            continue
        source = linecache.getline(summary.filename, summary.lineno or 1).strip()
        if not source:
            return None
        try:
            tree = ast.parse(source, mode='eval')
        except SyntaxError:
            return f'`{source}`'
        for node in ast.walk(tree):
            if not isinstance(node, ast.Subscript):
                continue
            if isinstance(node.value, ast.Name):
                name = node.value.id
                obj = frame.f_locals.get(name)
                if obj is None:
                    obj = frame.f_globals.get(name)
                if obj is not None:
                    return f'`{source}` — {name} is {_describe_container(obj)}'
            return f'`{source}`'
        return f'`{source}`'
    return None

def _index_error_context(tb) -> str | None:
    def fmt(obj, key):
        desc = _describe_container(obj)
        if key is not None and not isinstance(key, slice):
            return f'index {key} out of range for {desc}'
        return f'out of range for {desc}'
    return _subscript_error_context(tb, fmt)

def _key_error_context(tb) -> str | None:
    def fmt(obj, key):
        desc = _describe_container(obj)
        if key is not None:
            return f'key {key!r} not found in {desc}'
        return f'key not found in {desc}'
    return _subscript_error_context(tb, fmt)

def _is_playground_file(filename: str) -> bool:
    return filename.startswith('<playground-')

def _has_external_frames(tb) -> bool:
    """Returns True if any non-frplib, non-playground frames follow the last <module> frame.

    Takes a single parameter: a traceback produced by an exception in the repl.

    Used to decide whether to show the explain_error() hint alongside a clean
    error message — i.e., when the error is buried inside imported user code
    rather than being a direct top-level expression.

    """
    frames = list(tb_module.walk_tb(tb))
    last_module_idx = -1
    for i, (frame, _) in enumerate(frames):
        if (_is_playground_file(frame.f_code.co_filename)
                and frame.f_code.co_name == '<module>'):
            last_module_idx = i
    for frame, _ in frames[last_module_idx + 1:]:
        fname = frame.f_code.co_filename
        if not fname.startswith('<') and 'frplib' not in fname:
            return True
    return False

def _is_toplevel_in_repl(tb) -> bool:
    """Returns True if an exception originated directly at the REPL top level.

    Takes a single parameter: a traceback produced by an exception in the repl.

    """
    last_playground = None
    for frame, _lineno in tb_module.walk_tb(tb):
        if _is_playground_file(frame.f_code.co_filename):
            last_playground = frame
    return last_playground is not None and last_playground.f_code.co_name == '<module>'

def _is_explain_error_call(tb) -> bool:
    """Returns True if this traceback entry is a top-level explain_error() call.

    Takes a single parameter: a traceback produced by an exception in the repl.

    Uses linecache (populated by _compile_with_flags) to get the source line
    and checks via AST that it is a bare call to explain_error.

    """
    frame = tb.tb_frame
    if frame.f_code.co_name != '<module>':
        return False
    source = linecache.getline(frame.f_code.co_filename, tb.tb_lineno).strip()
    try:
        node = ast.parse(source, mode='eval').body
    except SyntaxError:
        return False
    return (isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == 'explain_error')


#
# REPL Definition
#

class PlaygroundRepl(PythonRepl):
    """Customized playground-specific ptpython repl manager. """

    # def __init__(self, *args, **kwargs) -> None:
    #     super().__init__(*args, **kwargs)
    #
    #     @self.add_key_binding("c-c", eager=True, filter=has_focus(self.default_buffer))
    #     def _(event) -> None:
    #         event.app.output.write("\rOperation Interrupted\n\n")
    #         event.app.output.flush()
    #         event.app.exit(exception=KeyboardInterrupt)

    def _compile_with_flags(self, code: str, mode: str):
        filename = f'<playground-{self.current_statement_index}>'
        result = compile(
            code, filename, mode,
            flags=self.get_compiler_flags(),
            dont_inherit=True,
        )
        lines = code.splitlines(keepends=True)
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'
        linecache.cache[filename] = (len(code), None, lines, filename)
        return result

    def _show_result(self, result: object) -> None:
        """Displays an evaluation result in appropriate form at the output.

        Specially renderable objects are displayed using their __frplib_repr__() method.
        Other objects are displayed in ordinary style.

        """
        if isinstance(result, Renderable) and not isinstance(result, type):
            # Don't call for classes e.g., VecTuple as a class not instance.
            # Write via environment.console (stdout). Blank-line handling is
            # done by run_and_show_expression in ptpython 3.0.32 after we return.
            try:
                environment.console.print(result.__frplib_repr__())
            except Exception as e:  # pylint: disable=broad-exception-caught
                environment.console.print(f'Could not print result due to an error:\n  {str(e)}')
        else:
            super()._show_result(result)    # type: ignore

    def _show_exception_trimmed(self, e: BaseException) -> None:
        """Runs ptpython's exception display but with leading internal frames removed.

        This eliminates frames that are only from the ptpython infrastructure that
        have no real diagnostic value to the user.

        """
        # Walk e.__traceback__ forward to the first playground frame,
        # skipping any leading explain_error() call frame as well.
        # If no playground frame, handle the exception by the standard route.
        trimmed = e.__traceback__
        while trimmed is not None and not _is_playground_file(trimmed.tb_frame.f_code.co_filename):
            trimmed = trimmed.tb_next
        if trimmed is None:
            super()._handle_exception(e)
            return
        if _is_explain_error_call(trimmed):
            trimmed = trimmed.tb_next

        # Temporarily setting e.__traceback__ to that point so display_exception shows only user frames.
        # Then restore the original. As such pdb.pm() is unaffected because
        # sys.last_traceback is set from sys.exc_info() at the original catch site.
        original = e.__traceback__
        e.__traceback__ = trimmed
        try:
            super()._handle_exception(e)
        finally:
            e.__traceback__ = original

    def _handle_subscript_error(self, e: BaseException, tb, label: str, context: str | None, default: str) -> None:
        """Provides a cleaner error message with source identification, with optional further explanation.

        Correctly distinguishes single expressions at the repl, functions defined at the repl,
        or functions defined in external code, giving appropriate source identification for
        each. In appropriate cases, it will suggest a call to explain_error() to get more
        detail from the stack.

        This is focused on Index and Key errors, which are both common user mistakes and
        also have identifiable points in the traceback for cleaning.

        """
        if _is_toplevel_in_repl(tb):
            hint = ('\nCall explain_error() for the full traceback.'
                    if _has_external_frames(tb) else '')
            environment.console.print(f'{label}: {context or default}{hint}')
        else:
            if context:
                original_args = e.args
                e.args = (context,)
                try:
                    self._show_exception_trimmed(e)
                finally:
                    e.args = original_args
            else:
                self._show_exception_trimmed(e)

    def _handle_exception(self, e: BaseException) -> None:
        self.get_globals()['_e'] = e

        if isinstance(e, FrplibException):
            try:
                environment.console.print(str(e))
            except Exception:   # pylint: disable=broad-exception-caught
                environment.console.print(f'FrplibException: {str(e)}')
        elif isinstance(e, (IndexError, KeyError)):
            # Subscript errors are among the most common in interactive use,
            # so we try to give good, meaningful error messages if possible.
            t, v, tb = sys.exc_info()
            sys.last_type, sys.last_value, sys.last_traceback = t, v, tb
            if isinstance(e, IndexError):
                label = 'Index Error'
                context = _index_error_context(tb)
                default = str(e) or 'index out of range'
            else:
                label = 'Key Error'
                context = _key_error_context(tb)
                default = f'key {e.args[0]!r} not found' if e.args else 'key not found'
            self._handle_subscript_error(e, tb, label, context, default)
        else:
            self._show_exception_trimmed(e)

    def _handle_keyboard_interrupt(self, e: KeyboardInterrupt) -> None:
        output = self.app.output

        output.write("\rOperation Interrupted\n\n")
        output.flush()

    def _add_to_namespace(self) -> None:
        """
        Add ptpython built-ins to global namespace.
        """
        globals = self.get_globals()

        # Add a 'get_ptpython', similar to 'get_ipython'
        def get_playground() -> PythonInput:
            return self

        def explain_error() -> None:
            "Show the full traceback for the most recent exception (_e)."
            err = globals.get('_e')
            if err is None:
                environment.console.print('No recent error stored.')
            else:
                self._show_exception_trimmed(err)

        self._injected_globals = [
            "get_playground",
            "info",
            "explain_error",
            "_running_in_playground"
        ]

        globals["get_playground"] = get_playground
        globals["info"] = info
        globals["explain_error"] = explain_error
        globals["_running_in_playground"] = True
        environment.interactive_mode()
        import_playground(globals)

    def _remove_from_namespace(self) -> None:
        """
        Remove added symbols from the globals.
        """
        globals = self.get_globals()
        for symbol in self._injected_globals:
            del globals[symbol]
        remove_playground(globals)
