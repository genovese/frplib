import re

from pathlib import Path
from typing                        import Callable

from prompt_toolkit                import PromptSession, print_formatted_text
from prompt_toolkit.document       import Document
from prompt_toolkit.formatted_text import to_formatted_text, FormattedText
from prompt_toolkit.history        import FileHistory
from prompt_toolkit.key_binding    import KeyBindings
from prompt_toolkit.lexers         import PygmentsLexer
from prompt_toolkit.styles         import Style
from parsy                         import (Parser,
                                           ParseError,
                                           alt,
                                           regex,
                                           seq,
                                           string,
                                           success,
                                           whitespace,
                                           )
from prompt_toolkit.validation     import Validator, ValidationError
from rich                          import print as rich_print

from frplib.env                    import environment
from frplib.exceptions             import MarketError
from frplib.frps                   import FrpDemoSummary
from frplib.kinds                  import Kind, kind
from frplib.kind_trees             import canonical_from_tree
from frplib.repls.market_lexer     import MarketCommandLexer
from frplib.parsing.parsy_adjust   import (generate,
                                           join_nl,
                                           parse_error_message,
                                           with_label
                                           )
from frplib.parsing.kind_strings   import (kind_sexp, integer_p, validate_kind)

# from rich.console import Console
# from rich.table   import Table
# console = Console(highlight=False)

#
# Basic Combinators
#

ws1 = with_label('whitespace', whitespace)
ws = ws1.optional()
count = with_label('an FRP count', integer_p)

price_re = r'\$?((?:0|[1-9][0-9]*)(\.[0-9]+)?(e[-+]?(?:0|[1-9][0-9]*))?)'
price = with_label('a price', regex(price_re, group=1).map(float))

with_kw = with_label('keyword "with"', string('with') << ws1)
kind_kw = with_label('keyword "kind"', string('kind') << ws)
kinds_kw = with_label('keyword "kinds"', string('kinds') << ws)

end_of_command = with_label('an end of command (".") character', string('.'))

#
# Market Command Parsers
#

@generate
def demo_command():
    yield ws
    frp_count = yield count
    yield ws1
    yield with_kw.optional()
    yield kind_kw.optional()
    kind = yield kind_sexp
    yield ws
    yield end_of_command
    return ('demo', frp_count, kind)   # ATTN: Change this to a dict

@generate
def show_command():
    yield ws1
    yield kind_kw.optional()
    kind = yield kind_sexp
    yield ws
    yield end_of_command
    return ('show', kind)   # ATTN: Change this to a dict

@generate
def buy_command():
    yield ws1
    frp_count = yield count
    yield ws
    yield string('@')
    yield ws
    prices = yield price.sep_by(seq(string(','), ws), min=1)
    yield ws
    yield with_kw.optional()
    yield kind_kw.optional()
    kind = yield kind_sexp
    yield ws
    yield end_of_command
    return ('buy', frp_count, prices, kind)   # ATTN: Change this to a dict

@generate
def compare_command():
    yield ws1
    frp_count = yield count
    yield ws1
    yield with_kw.optional()
    yield kinds_kw.optional()
    kind1 = yield kind_sexp
    yield ws
    kind2 = yield kind_sexp
    yield ws
    yield end_of_command
    return ('compare', frp_count, kind1, kind2)   # ATTN: Change this to a dict

@generate
def help_command():
    topic = yield with_label('topic', ws1 >> regex(r'[^.]+')).optional()
    topic = topic or ''
    yield ws >> end_of_command
    return ('help', re.sub(r'\r?\n', ' ', topic).strip())

exit_command = (success('exit') << end_of_command).map(lambda x: (x,))

command_parsers = {
    'demo': demo_command,
    'show': show_command,
    'buy':  buy_command,
    'help': help_command,
    'exit': exit_command,
    'quit': exit_command,
    'compare': compare_command,
}

def cmd_token(cmd_name: str) -> Parser:
    return string(cmd_name)

command = with_label(join_nl([f'"{k}"' for k in command_parsers],
                             prefixes=['a command ', 'either command ', 'one of the commands ']),
                     alt(*[cmd_token(k) for k in command_parsers]))
command = command.bind(lambda cmd: command_parsers[cmd])


#
# Validation
#

class CommandValidator(Validator):
    def validate(self, document):
        text = document.text
        if text and text.endswith('.'):
            try:
                cmd_info = command.parse(text)
                if cmd_info[0] == 'demo' or cmd_info[0] == 'buy':
                    kind_validation = validate_kind(cmd_info[-1])
                else:
                    kind_validation = ''
                if kind_validation:
                    raise ValidationError(message=kind_validation.replace('\n', ' '),
                                          cursor_position=text.find('('))
            except ParseError as e:
                # mesg = environment.console_str(parse_error_message(e))
                mesg = parse_error_message(e, rich=False, short=True)
                raise ValidationError(message=mesg.replace('\n', ''),
                                      cursor_position=e.index)
                # with console.capture() as capture:
                #     console.print(parse_error_message(e))
                # raise ValidationError(message=capture.get().replace('\n', ''),
                #                       cursor_position=e.index)


#
# Rich Text I/O
#

def emit(*a, **kw) -> None:
    # print_formatted_text(*a, **kw)
    # rich_print(*a, **kw)
    environment.console.print(*a, **kw)

command_style = Style.from_dict({  # ATTN:TEMP Colors for teting
    'pygments.command': "steelblue bold",
    'pygments.connective': "#777777",  # "#430363",
    'pygments.kind': "#777777",   # "#430363",
    'pygments.operator': "gray",
    'pygments.punctuation': "#704000",
    'pygments.count': "#91011e",
    'pygments.node': "#0240a3",
    'pygments.weight': "#047d40 italic",  # "#016935",
    'pygments.other':  "black",
    'prompt': "#4682b4",
    'parse.parsed': '#71716f',
    'parse.error': '#ff0f0f bold',
    '': 'black',
})

def continuation_prompt(prompt_width: int, line_number: int, wrap_count: int) -> FormattedText:
    return to_formatted_text(PROMPT2 + ' ' * (prompt_width - 4), style='class:prompt')

PROMPT1 = 'market> '
PROMPT2 = '...>'


#
# Key Bindings
#

market_bindings = KeyBindings()
@market_bindings.add('enter')
def _(event):
    doc: Document = event.current_buffer.document
    if doc.text.endswith('.'):  # doc.char_before_cursor == '.' and doc.is_cursor_at_the_end:
        event.current_buffer.validate_and_handle()
    else:
        event.current_buffer.insert_text('\n')

@market_bindings.add('escape', 'enter')
def _(event):
    doc: Document = event.current_buffer.document
    if doc.char_before_cursor == '.' and doc.is_cursor_at_the_end:
        event.current_buffer.validate_and_handle()
    else:
        event.current_buffer.insert_text('\n')

@market_bindings.add('(')
def _(event):
    event.current_buffer.insert_text('(')
    event.current_buffer.insert_text(')', move_cursor=False)

@market_bindings.add(')')
def _(event):
    event.current_buffer.insert_text(')', overwrite=True)

@market_bindings.add('<')
def _(event):
    event.current_buffer.insert_text('<')
    event.current_buffer.insert_text('>', move_cursor=False)

@market_bindings.add('>')
def _(event):
    event.current_buffer.insert_text('>', overwrite=True)


#
# Command Handlers
#

def demo_handler(count, kind_tree) -> None:
    canonical = canonical_from_tree(kind_tree)
    k: Kind = kind(canonical)
    summary = FrpDemoSummary()
    for sample in k.sample(count):
        summary.add(sample)
    emit(f'Activated {count} FRPs with kind')
    emit(k.__frplib_repr__())
    emit(summary)

def buy_handler(count, prices, kind_tree) -> None:
    pass

def compare_handler(count, kind_tree1, kind_tree2) -> None:
    pass

def show_handler(kind_tree) -> None:
    k: Kind = kind(canonical_from_tree(kind_tree))
    # ATTN: Replace with the unfolded version
    # ATTN: Add *a, *kw to frplib_repr ?
    emit(k.__frplib_repr__())

def help_handler(topic) -> None:
    pass

def default_handler(*a, **kw) -> None:
    raise MarketError('I do not know what to do as I did not recognize that command.')

dispatch: dict[str, Callable[..., None]] = {
    'demo': demo_handler,
    'buy': buy_handler,
    'compare': compare_handler,
    'show': show_handler,
    'help': help_handler,
    '_': default_handler,
}

#
# Main Entry Point
#

def main() -> None:
    lexer = PygmentsLexer(MarketCommandLexer)
    session: PromptSession = PromptSession(
        multiline=True,
        lexer=lexer,
        prompt_continuation=continuation_prompt,
        style=command_style,
        key_bindings=market_bindings,
        history=FileHistory(str(Path.home() / ".frp-market-history")),
        validator=CommandValidator(),  # This works but only gives one line; needs alternative formatting
    )
    abort_count = 0

    while True:
        try:
            text = session.prompt(PROMPT1)
        except KeyboardInterrupt:
            # # with console.capture() as capture:
            # #     console.print("[bold red]Hello[/] World")
            # # print(capture.get())
            # # rich_print("Say [bold blue]hello[/] world!")
            #
            # table = Table(title="Star Wars Movies")
            #
            # table.add_column("Released", justify="right", style="cyan", no_wrap=True)
            # table.add_column("Title", style="magenta")
            # table.add_column("Box Office", justify="right", style="green")
            #
            # table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
            # table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
            # table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889")
            # table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889")
            # rich_print(table)
            abort_count += 1
            if abort_count > 2:
                exit(0)
            continue
        abort_count = 0
        if re.match(r'^\s*$', text):
            continue
        try:
            cmd_info = command.parse(text)
            if cmd_info[0] == 'exit':
                exit(0)

            dispatch[cmd_info[0]](*cmd_info[1:])
        except ParseError as e:
            emit('There was a problem with the last command.')
            emit(parse_error_message(e))  # , style=command_style)


if __name__ == '__main__':
    main()
