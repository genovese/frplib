from __future__ import annotations

import builtins

from ptpython.repl     import PythonRepl
from typing            import Callable, ContextManager, Protocol
from typing_extensions import Any

from prompt_toolkit.patch_stdout      import patch_stdout as patch_stdout_context
from prompt_toolkit.utils             import DummyContext

_Namespace = dict[str, Any]
_GetNamespace = Callable[[], _Namespace]

# from prompt_toolkit.completion        import Completer
# from prompt_toolkit.input             import Input
# from prompt_toolkit.key_binding       import KeyBindings
# from prompt_toolkit.layout.containers import AnyContainer
# from prompt_toolkit.lexers            import Lexer
# from prompt_toolkit.output            import ColorDepth, Output
# from prompt_toolkit.patch_stdout      import patch_stdout as patch_stdout_context
# from prompt_toolkit.utils             import DummyContext
# from prompt_toolkit.validation        import Validator
#
# class InputMaker(Protocol):
#     def __call__(
#             self,
#             # PythonInput parameters
#             get_globals: _GetNamespace | None = None,
#             get_locals: _GetNamespace | None = None,
#             history_filename: str | None = None,
#             vi_mode: bool = False,
#             color_depth: ColorDepth | None = None,
#             # Input/output.
#             input: Input | None = None,
#             output: Output | None = None,
#             # For internal use.
#             extra_key_bindings: KeyBindings | None = None,
#             create_app: bool = True,
#             _completer: Completer | None = None,
#             _validator: Validator | None = None,
#             _lexer: Lexer | None = None,
#             _extra_buffer_processors=None,
#             _extra_layout_body: AnyContainer | None = None,
#             _extra_toolbars=None,
#             _input_buffer_height=None,
#     ) -> PythonRepl:
#         ...

class ReplMaker(Protocol):
    "The minimal callable signature used by `embed` to create a PythonRepl."
    def __call__(
            self,
            # PythonInput parameters
            get_globals: _GetNamespace | None = None,
            get_locals: _GetNamespace | None = None,
            history_filename: str | None = None,
            vi_mode: bool = False,
            # PythonRepl parameters
            startup_paths=None,
    ) -> PythonRepl:
        ...

def embed(
        globals=None,
        locals=None,
        configure: Callable[[PythonRepl], None] | None = None,
        vi_mode: bool = False,
        history_filename: str | None = None,
        title: str | None = None,
        startup_paths=None,
        patch_stdout: bool = False,
        return_asyncio_coroutine: bool = False,
        make_repl: ReplMaker = PythonRepl,
) -> None:
    """
    Call this to embed  Python shell at the current point in your program.
    It's similar to `IPython.embed` and `bpython.embed`. ::

        from prompt_toolkit.contrib.repl import embed
        embed(globals(), locals())

    :param vi_mode: Boolean. Use Vi instead of Emacs key bindings.
    :param configure: Callable that will be called with the `PythonRepl` as a first
                      argument, to trigger configuration.
    :param title: Title to be displayed in the terminal titlebar. (None or string.)
    :param patch_stdout:  When true, patch `sys.stdout` so that background
        threads that are printing will print nicely above the prompt.
    """
    # Default globals/locals
    if globals is None:
        globals = {
            "__name__": "__main__",
            "__package__": None,
            "__doc__": None,
            "__builtins__": builtins,
        }

    locals = locals or globals

    def get_globals():
        return globals

    def get_locals():
        return locals

    # Create REPL.
    repl = make_repl(
        get_globals=get_globals,
        get_locals=get_locals,
        vi_mode=vi_mode,
        history_filename=history_filename,
        startup_paths=startup_paths,
    )

    if title:
        repl.terminal_title = title

    if configure:
        configure(repl)

    # Start repl.
    patch_context: ContextManager[None] = (
        patch_stdout_context() if patch_stdout else DummyContext()
    )

    if return_asyncio_coroutine:

        async def coroutine() -> None:
            with patch_context:
                await repl.run_async()

        return coroutine()  # type: ignore
    else:
        with patch_context:
            repl.run()
