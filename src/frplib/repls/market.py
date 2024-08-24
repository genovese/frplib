from __future__ import annotations

import re

from importlib.resources           import files
from pathlib                       import Path
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
from rich.table                    import Table
from rich                          import box as rich_box

from frplib.env                    import environment
from frplib.exceptions             import MarketError
from frplib.frps                   import FrpDemoSummary
from frplib.kinds                  import Kind, kind
from frplib.kind_trees             import (canonical_from_tree, unfolded_labels,
                                           unfold_scan, unfolded_str)
from frplib.numeric                import Numeric, as_real, show_tuples, show_values
from frplib.output                 import in_panel
from frplib.repls.market_lexer     import MarketCommandLexer
from frplib.parsing.parsy_adjust   import (generate,
                                           join_nl,
                                           parse_error_message,
                                           with_label
                                           )
from frplib.parsing.kind_strings   import (kind_sexp, integer_p, validate_kind)
from frplib.vec_tuples             import VecTuple

# from rich         import print as rich_print
# from rich.console import Console
# from rich.table   import Table


#
# Basic Combinators
#

ws1 = with_label('whitespace', whitespace)
ws = ws1.optional()
count = with_label('an FRP count', integer_p)

price_re = r'\$?(-?(?:0|[1-9][0-9]*)(\.[0-9]+)?(e[-+]?(?:0|[1-9][0-9]*))?)'
price = with_label('a price', regex(price_re, group=1).map(float))

with_kw = with_label('keyword "with"', string('with') << ws1)
kind_kw = with_label('keyword "kind"', string('kind') << ws)
kinds_kw = with_label('keyword "kinds"', string('kinds') << ws)
and_kw = with_label('keyword "and"', string('and') << ws)

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
    yield and_kw.optional()
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

exit_command = (success('exit') << ws << end_of_command).map(lambda x: (x,))

command_parsers = {
    'demo': demo_command,
    'show': show_command,
    'buy':  buy_command,
    'compare': compare_command,
    'help': help_command,
    'exit': exit_command,
    'quit': exit_command,
    'done': exit_command,
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
        if text and re.search(r'\.\s*$', text):  # text.endswith('.'):
            try:
                cmd_info = command.parse(text)
                if cmd_info[0] == 'demo' or cmd_info[0] == 'buy' or cmd_info[0] == 'show':
                    kind_validation = validate_kind(cmd_info[-1])
                elif cmd_info[0] == 'compare':
                    kind_validation = validate_kind(cmd_info[-2]) + validate_kind(cmd_info[-1])
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
    environment.console.print(*a, **kw)

# Color themes for bright and dark terminals
bright_theme = {
    'pygments.command': "steelblue bold",
    'pygments.connective': "#777777",  # "#430363",
    'pygments.kind': "#777777",   # "#430363",
    'pygments.operator': "gray",
    'pygments.punctuation': "#704000",
    'pygments.count': "#91011e",
    'pygments.node': "#0240a3",
    'pygments.weight': "#047d40 italic",  # "#016935",
    'pygments.other': 'black',
    'prompt': "#4682b4",
    'parse.parsed': '#71716f',
    'parse.error': '#ff0f0f bold',
    '': 'black',
}

dark_theme = {
    'pygments.command': "#b97d4b bold",
    'pygments.connective': "#888888",  # "#bcfc9c",
    'pygments.kind': '#888888',   # "#bcfc9c",
    'pygments.operator': "gray",
    'pygments.punctuation': '#8fbfff',
    'pygments.count': '#6efee1',
    'pygments.node': '#fdbf5c',
    'pygments.weight': "#fb82bf italic",  # "#fe96ca",
    'pygments.other': 'white',
    'prompt': '#b97d4b',
    'parse.parsed': '#8e8e90',
    'parse.error': '#00f0f0 bold',
    '': 'white',
}

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
    if re.search(r'\.\s*$', doc.text):
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
    """Simulates the activation of `count` FRPs with kind given by `kind_tree`.

    `count` is a positive integer
    `kind_tree` is a sexp-formatted kind tree encoded in lists.
        It is the result of successful parsing by frplib.parsing.kind_strings.kind_sexp.

    Emits a picture of the kind summary table of the simulation result.

    """
    canonical = canonical_from_tree(kind_tree)
    k: Kind = kind(canonical)
    summary = FrpDemoSummary()
    for sample in k.sample(count):
        summary.add(sample)
    emit(f'Activated {count} FRPs with kind')
    show_handler(kind_tree)
    # emit(k.__frplib_repr__())
    emit(summary.table(environment.ascii_only))

def buy_handler(count: int, prices: list[float], kind_tree: list) -> None:
    """Simulates the purchase, activation, and observation of FRPs.

    `count` is the number of FRPs to purchase at each price.
        It should be positive.
    `prices` is a list of prices (floats) at which batches of size `count`
        will be purchased
    `kind_tree` specifies the kind of FRPs being purchased. It is
        is a sexp-formatted kind tree encoded in lists, as parsed by
        frplib.parsing.kind_strings.kind_sexp.

    Emits a table summarizing the simulation, giving the Price/Unit,
    the Net Payoff, and the Net Payoff/Unit.

    """
    if count <= 0:
        return

    canonical = canonical_from_tree(kind_tree)
    k: Kind = kind(canonical)

    prices.sort()

    real_prices: list[Numeric] = []
    net_payoffs: list[VecTuple] = []
    net_per_unt: list[VecTuple] = []
    n = as_real(count)
    for price in prices:
        real_price: Numeric = as_real(price)
        total: VecTuple = sum(k.sample(count))
        net: VecTuple = total - n * real_price
        per_unit: VecTuple = net / n

        real_prices.append(real_price)
        net_payoffs.append(net)
        net_per_unt.append(per_unit)
        # fields = {
        #     'price': nroundx(real_price, mask=as_real('1.00')),
        #     'net': net,
        #     'net-per-unit': per_unit
        #     'ps':
        # }
        # widths = (0, 0, 0)
        # widths = tuple(map(max, zip(widths, (fields['price'], fields['net'], fields['net/u']))))
        # payoffs.append(fields)

    real_prices_s = show_values(real_prices, max_denom=1)
    net_payoffs_s = show_tuples(net_payoffs, max_denom=1)
    net_per_unt_s = show_tuples(net_per_unt, max_denom=1)

    emit(f'Buying {int(count):,} FRPs with kind')
    show_handler(kind_tree)
    # emit(k.__frplib_repr__())
    emit('at each price')

    if environment.ascii_only:
        out: list[str] = []
        for i in range(len(prices)):
            out.append("  {price:<12}  {net:>16}    {perunit:>12}".format(
                price='$' + real_prices_s[i],
                net='$' + net_payoffs_s[i],
                perunit='$' + net_per_unt_s[i]
            ))

        header = "{price:<12}{net:>26} {perunit:>12}".format(
            price='Price/Unit',
            net='Net Payoff',
            perunit='Net Payoff/Unit'
        )
        emit(header + '\n' + "\n".join(out))
    else:
        # ATTN: Put styles in a more central place (environment?), e.g., environment.styles['values']
        table = Table(box=rich_box.SQUARE_DOUBLE_HEAD)
        table.add_column('Price/Unit ($)', justify='right', style='#4682b4', no_wrap=True)
        table.add_column('Net Payoff ($)', justify='right')
        table.add_column('Net Payoff/Unit ($)', justify='right', style='#6a6c6e')

        for i in range(len(prices)):
            table.add_row(
                real_prices_s[i],
                net_payoffs_s[i],
                net_per_unt_s[i]
            )
        emit(table)

def compare_handler(count, kind_tree1, kind_tree2) -> None:
    canonical1 = canonical_from_tree(kind_tree1)
    canonical2 = canonical_from_tree(kind_tree2)
    k1: Kind = kind(canonical1)
    k2: Kind = kind(canonical2)

    emit(f'Comparing {count} activated FRPs each for two kinds, A and B.')

    emit(in_panel(show_kind_tree(kind_tree1), title='Kind A'))
    emit(in_panel(show_kind_tree(kind_tree2), title='Kind B'))

    for k, which in [(k1, 'A'), (k2, 'B')]:
        summary = FrpDemoSummary()
        for sample in k.sample(count):
            summary.add(sample)
        emit(summary.table(environment.ascii_only, title=f'Summary of Demo for Kind {which}'))

def show_kind_tree(kind_tree) -> str:
    "Convert a kind tree to text; the tree need not be canonical."
    def _find_dims(xs):
        for x in xs:
            if isinstance(x, list):
                yield from _find_dims(x)
            elif isinstance(x, tuple):
                yield len(x)

    dim = max(_find_dims(kind_tree))
    wd = [(0, 3)]  # Widths of the root node weight and value
    labelled = unfolded_labels(kind_tree[1:], str(kind_tree[0]), 1, wd)
    # ATTN: In case of dim bigger than max level, adjust sep
    sep = [2 * (dim - level) for level in range(dim + 1)]  # seps should be even
    scan, _ = unfold_scan(labelled, wd, sep)

    return unfolded_str(scan, wd)

def show_handler(kind_tree) -> None:
    "Display a kind tree in text format; the tree need not be canonical."
    emit(in_panel(show_kind_tree(kind_tree)))

def help_handler(topic) -> None:
    if not topic:
        overview = files('frplib.data').joinpath('market-help-overview.txt').read_text()
        emit(overview)
    else:
        try:
            clean_topic = re.sub(r'[^-A-Za-z_0-9]', '', topic)
            guidance = files('frplib.data').joinpath(f'market-help-{clean_topic}.txt').read_text()
            emit(guidance)
        except Exception:
            emit(f'I\'m sorry, but I do not have any guidance on {topic}. '
                 'Try "help." or "help help". for an overview of topics.')

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
    command_style = Style.from_dict(dark_theme if environment.dark_mode else bright_theme)
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
            emit(parse_error_message(e))


if __name__ == '__main__':
    main()
