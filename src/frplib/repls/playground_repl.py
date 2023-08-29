from __future__ import annotations

from importlib                     import import_module
from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.shortcuts      import print_formatted_text
from ptpython.repl                 import PythonRepl
from ptpython.python_input         import PythonInput

from frplib.env        import environment
from frplib.exceptions import FrplibException
from frplib.protocols  import Renderable

def info(topic: str = '') -> None:
    print_formatted_text(HTML('<violet>This is useful information. More coming soon!</violet>'))

playground_imports: dict[str, list[str]] = {
    # When there are submodules loaded, order from parent down
    # Note that symbols and module names cannot be the same
    # as we are adding both to globals()
    # ATTN: Consider *not* adding the module names to globals
    'kinds': [
        'Kind', 'kind', 'unfold', 'conditional_kind',
        'constant', 'uniform', 'either', 'symmetric',
        'weighted_by',
        'integers', 'evenly_spaced', 'bin',
        'without_replacement', 'subsets', 'permutations_of',
    ],
    'statistics': [
        'Statistic', 'Condition', 'MonoidalStatistic',
        'is_statistic', 'statistic', 'scalar_statistic',
        'tuple_safe', 'infinity',
        'fork', 'chain', 'compose',
        'Id', 'Scalar', '__', 'Proj',
        'Sum', 'Count', 'Max', 'Min', 'Mean', 'Abs',
        'Constantly', 'Fork', 'ForEach', 'IfThenElse',
        'And', 'Or', 'Not',
    ],
    'expectations': ['E'],
    'frps': [
        'FRP', 'frp', 'conditional_frp'
    ],
    'utils': [
        'clone', 'compose', 'identity', 'index_of', 'irange',
        'values', 'dim', 'codim', 'size',
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

def remove_playground(globals) -> None:
    modules = playground_imports.keys()
    for module_name in modules:
        for symbol_name in playground_imports[module_name]:
            if symbol_name in globals:
                del globals[symbol_name]
        if module_name in globals:
            del globals[module_name]

class PlaygroundRepl(PythonRepl):
    def show_result(self, result: object) -> None:
        """
        Show __repr__ for an `eval` result and print to output.
        """
        if isinstance(result, Renderable) and not isinstance(result, type):
            # Don't call for classes e.g., VecTuple as a class not instance
            # Holding off on pager for now
            environment.console.print(result.__frplib_repr__())
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
