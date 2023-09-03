#!/usr/bin/env python
"""
A stub for the playground app, which will actually be a subcommand.
"""

from __future__ import annotations

from pathlib import Path

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts      import print_formatted_text as print
from ptpython.prompt_style         import PromptStyle

from frplib.env                    import environment
from frplib.repls.playground_repl  import PlaygroundRepl
from frplib.repls.ptembed          import embed


def style_prompt_bright(text):
    return f'<steelblue>{text}</steelblue>'

def style_prompt_dark(text):
    return f'<style fg="#b97d4b">{text}</style>'

def configure(repl):
    # Probably, the best is to add a new PromptStyle to `all_prompt_styles` and
    # activate it. This way, the other styles are still selectable from the
    # menu.
    class CustomPrompt(PromptStyle):
        def in_prompt(self):
            style_prompt = style_prompt_dark if environment.dark_mode else style_prompt_bright
            return HTML(style_prompt("playground&gt; "))

        def in2_prompt(self, width):
            style_prompt = style_prompt_dark if environment.dark_mode else style_prompt_bright
            return HTML(style_prompt("...&gt; ".ljust(width)))

        def out_prompt(self):
            return []

    repl.all_prompt_styles["playground"] = CustomPrompt()
    repl.prompt_style = "playground"
    repl.show_signature = False
    repl.show_docstring = True
    repl.enable_syntax_highlighting = True
    repl.highlight_matching_parenthesis = True

    if environment.dark_mode:
        repl.use_code_colorscheme("github-dark")
    else:
        repl.use_code_colorscheme("default")

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
