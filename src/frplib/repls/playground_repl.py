from __future__ import annotations

from importlib                     import import_module
from importlib.resources           import files

from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.shortcuts      import print_formatted_text
from ptpython.repl                 import PythonRepl
from ptpython.python_input         import PythonInput
from rich.markdown                 import Markdown

from frplib.env        import environment
from frplib.exceptions import FrplibException
from frplib.protocols  import Renderable


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
        'constant', 'uniform', 'either',
        'symmetric', 'linear', 'geometric',
        'weighted_by', 'weighted_as', 'weighted_pairs',
        'arbitrary', 'integers', 'evenly_spaced', 'bin',
        'without_replacement', 'subsets', 'permutations_of',
    ],
    'statistics': [
        'Statistic', 'Condition', 'MonoidalStatistic',
        'is_statistic', 'statistic', 'condition', 'scalar_statistic',
        'tuple_safe', 'infinity', 'is_true', 'is_false',
        'fork', 'chain', 'compose', 'scalar_fn',
        'Id', 'Scalar', '__', 'Proj', '_x_',
        'Sum', 'Product', 'Count', 'Max', 'Min', 'Abs', 'SumSq',
        'Sqrt', 'Floor', 'Ceil', 'NormalCDF',
        'Exp', 'Log', 'Log2', 'Log10',
        'Sin', 'Cos', 'Tan', 'ATan2', 'Sinh', 'Cosh', 'Tanh',
        'Pi', 'FromDegrees', 'FromRadians',
        'Mean', 'StdDev', 'Variance',
        'SumSq', 'Norm', 'Dot',
        'ArgMin', 'ArgMax', 'Ascending', 'Descending',
        'Diff', 'Diffs', 'Permute',
        'Constantly', 'Fork', 'MFork', 'ForEach', 'IfThenElse',
        'And', 'Or', 'Not', 'Xor', 'top', 'bottom',
    ],
    'expectations': ['E', 'Var', 'D_'],
    'frps': [
        'FRP', 'frp', 'conditional_frp', 'is_frp', 'evolve', 'shuffle',
    ],
    'calculate': ['substitute', 'substitute_with', 'substitution'],
    'numeric': ['numeric_exp', 'numeric_ln', 'numeric_log10', 'numeric_log2',
                'numeric_abs', 'numeric_sqrt', 'numeric_floor', 'numeric_ceil'],
    'quantity': ['as_quantity', 'qvec'],
    'symbolic': ['gen_symbol', 'is_symbolic', 'is_zero', 'symbol', 'symbols'],
    'utils': [
        'clone', 'compose', 'const', 'every', 'frequencies',
        'identity', 'index_of', 'index_where', 'irange', 'iterate', 'lmap',
        'values', 'dim', 'codim', 'size', 'typeof', 'show', 'some',
    ],
    'vec_tuples': [
        'VecTuple',
        'as_numeric_vec', 'as_scalar', 'as_vec_tuple',
        'is_vec_tuple', 'vec_tuple',
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
# REPL Definition
#

class PlaygroundRepl(PythonRepl):
    def show_result(self, result: object) -> None:
        """
        Show __repr__ for an `eval` result and print to output.
        """
        if isinstance(result, Renderable) and not isinstance(result, type):
            # Don't call for classes e.g., VecTuple as a class not instance
            # Holding off on pager for now
            try:
                environment.console.print(result.__frplib_repr__())
            except Exception as e:
                environment.console.print(f'Could not print result due to an error: {str(e)}')
        else:
            formatted_text_output = self._format_result_output(result)

            if self.enable_pager:
                self.print_paginated_formatted_text(formatted_text_output)
            else:
                self.print_formatted_text(formatted_text_output)

        self.app.output.flush()
        if self.insert_blank_line_after_output:
            self.app.output.write("\n")

    def _handle_exception(self, e: BaseException) -> None:
        output = self.app.output

        if isinstance(e, FrplibException):
            # ATTN
            print_formatted_text(
                ANSI(environment.console_str(str(e))),
                output=output
            )
        else:
            tokens = self._format_exception_output(e)

            print_formatted_text(
                tokens,
                style=self._current_style,
                style_transformation=self.style_transformation,
                include_default_pygments_style=False,
                output=output,
            )
        output.flush()

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

        self._injected_globals = [
            "get_playground",
            "info",
            "_running_in_playground"
        ]

        globals["get_playground"] = get_playground
        globals["info"] = info
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
