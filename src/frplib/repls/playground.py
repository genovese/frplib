#!/usr/bin/env python
"""
A stub for the playground app, which will actually be a subcommand.
"""

from __future__ import annotations

from pathlib import Path

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts      import print_formatted_text as print
from ptpython.prompt_style         import PromptStyle

from frplib.repls.playground_repl  import PlaygroundRepl
from frplib.repls.ptembed          import embed

def configure(repl):
    # Probably, the best is to add a new PromptStyle to `all_prompt_styles` and
    # activate it. This way, the other styles are still selectable from the
    # menu.
    class CustomPrompt(PromptStyle):
        def in_prompt(self):
            return HTML("<steelblue>playground&gt;</steelblue> ")

        def in2_prompt(self, width):
            return "...> ".ljust(width)

        def out_prompt(self):
            return []

    repl.all_prompt_styles["playground"] = CustomPrompt()
    repl.prompt_style = "playground"
    repl.show_signature = False
    repl.show_docstring = True
    repl.enable_syntax_highlighting = True
    repl.highlight_matching_parenthesis = True

    # Title in status bar
    repl.title = HTML('<style fg="#0099ff"><b>FRP Playground</b></style> ')

def main():
    try:
        embed(
            globals(),
            locals(),
            title='FRP Playground',
            configure=configure,
            make_repl=PlaygroundRepl,
            history_filename=str(Path.home() / ".frp-playground-history")
        )
    except SystemExit:
        pass
    print('Playground finished')


if __name__ == "__main__":
    main()
