"""Interactive info system for use in playground repl."""

# pylint: disable=too-many-locals, too-many-branches, too-many-statements, import-outside-toplevel

from __future__          import annotations

import re

from collections.abc     import Callable
from importlib.resources import as_file, files
from typing              import TYPE_CHECKING, cast, Final

from prompt_toolkit.application          import Application
from prompt_toolkit.application.current  import get_app
from prompt_toolkit.completion           import Completer, Completion, FuzzyWordCompleter
from prompt_toolkit.formatted_text       import HTML
from prompt_toolkit.key_binding          import KeyBindings
from prompt_toolkit.layout.containers    import HSplit
from prompt_toolkit.layout.dimension     import D
from prompt_toolkit.layout.layout        import Layout
from prompt_toolkit.shortcuts            import PromptSession, print_formatted_text
from prompt_toolkit.validation           import ValidationError, Validator
from prompt_toolkit.widgets              import Label, RadioList, TextArea

from rich.markdown import Markdown

from frplib.env              import environment
from frplib.exceptions       import PlaygroundError
from frplib.data.info_tree   import info_tree
from frplib.repls.info_types import InfoNode, InfoTree


__all__ = ['info_interactive', 'menu_select_via_dialog', 'menu_select_via_completion']


#
# Data
#

BACK_LABEL = "⬅ Go Back"
NAV_HINT = "type to filter  ·  arrows or C-n/C-p to navigate  ·  Enter to select  ·  C-c to cancel"
NO_MATCH: Final[str] = "\x00no-match\x00"  # sentinel for empty-filter placeholder


#
# Helpers
#

def html_escape(text: str) -> str:
    """Returns string with basic HTML escapes for &, <, and >."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def is_subsequence(query: str, candidate: str) -> bool:
    """Is query string a sub-sequence of chars in candidate string?"""
    it = iter(candidate)
    return all(ch in it for ch in query)

def fuzzy_match(query, choices):
    """Basic case-insensitive fuzzy search of query string in list of choices."""
    if not query:
        return choices
    query = query.lower()
    return sorted((c for c in choices if is_subsequence(query, c.lower())), key=len)

def match_unique(text: str, choices: list[str]) -> str | None:
    """Returns the matching choice for text, or None if ambiguous or no match.

    Accepts an exact match or a fuzzy query that matches exactly one choice.
    Matching is case insensitive.

    """
    if text in choices:
        return text
    matches = fuzzy_match(text.lower(), choices)
    return matches[0] if len(matches) == 1 else None


#
# Helper Classes for Completion and Validation
#

class FuzzyAllCompleter(Completer):
    """FuzzyWordCompleter that returns all choices when the query is empty."""

    def __init__(self, words: list[str]) -> None:
        self._words = words
        self._fuzzy = FuzzyWordCompleter(words)

    def get_completions(self, document, complete_event):
        if document.text_before_cursor:
            yield from self._fuzzy.get_completions(document, complete_event)
        else:
            for word in self._words:
                yield Completion(word, start_position=0)

class ChoiceValidator(Validator):
    """Validator that accepts exact matches, unique fuzzy matches, and (optionally) empty input."""

    def __init__(self, choices: list[str], allow_empty: bool = False) -> None:
        self._choices = choices
        self._allow_empty = allow_empty

    def validate(self, document):
        if self._allow_empty and not document.text:
            return
        if match_unique(document.text, self._choices) is None:
            raise ValidationError(
                message="No unique match — type more or use navigation keys to select",
                cursor_position=len(document.text),
            )


#
# Menu Selection Methods
#

def menu_select_via_dialog(root_data: InfoTree, action: Callable | None, **kwds) -> list[tuple[str, InfoNode]]:
    """Interactive selection in multi-level menu with a prompt_toolkit dialog.

    User types to filter the candidate list and presses enter to select.
    The current default choice is marked and can be selected by enter
    at any point.

    Features:
      + Performs fuzzy search of remaining candidates as user types.
      + Includes a Back option at every level
      + Non-leaf loads can be designated as endpoints
      + Executes functions at endpoint nodes with current path as argument

    This is designed for use within a ptpython-based repl.
    It does not allow for key-based navigation, unfortunately;
    see menu_select_via_completion for an alternative interface.

    Parameter ROOT_DATA is a nested dictionary that represents the
    menu structure. Keys are either strings or None, with latter
    indicating that the current node is also a valid endpoint, even
    if it has children. Dictionary values are either child dicts or
    callables or None. A node whose value is callable is an endpoint
    (leaf node), and the callable is invoked with the current 'path'
    (list of keys to that point in the menu) and any keyword-only
    arguments given to this function. A node whose value is
    None is an endpoint (leaf node), and the function returns. A
    node whose value is a dict is a branch node and generates
    another selection at the next level. Any other type of value in
    the dict is ignored and treated as None.

    Returns None if the endpoint is a callable or the leaf node's
    path otherwise.

    """
    try:
        get_app()
    except Exception as e:
        raise PlaygroundError(str(e)) from e

    path: list[tuple[str, InfoNode]] = []
    current_data: InfoTree = root_data

    while True:
        # Build choices: self-endpoint first, then back, then children
        if not path:  # Top level
            msg = "Type to filter, Enter to select:"
            self_endpoint = []
            base_choices = [k for k in current_data if not k.startswith('_')]
        else:
            current_key, current_node = path[-1]
            self_endpoint = [f"◉ {current_key}"] if current_node.get('filepath', None) else []
            breadcrumb = " ➔ ".join(node[0] for node in path)
            msg = f"[{breadcrumb}]  Type to filter, Enter to select:"
            base_choices = (
                self_endpoint
                + [BACK_LABEL]
                + [k for k in current_data if not k.startswith('_')]
                # ^^^ ATTN: can add the description to the label here and above, eg., make_label(...)
            )

        # Sub-Widgets of the list display
        header = Label(msg)
        search_field = TextArea(prompt="➔ ", multiline=False, height=1, focusable=True)
        radio_choices = [(c, c) for c in base_choices]
        menu_list = RadioList(values=radio_choices)

        # Real-time fuzzy filtering: keep current_value synced to the top
        # of the filtered list so the (*) marker is always consistent.
        def on_text_changed(_):
            query = search_field.text
            filtered = fuzzy_match(query, base_choices)
            if filtered:
                menu_list.values = [(c, c) for c in filtered]
                menu_list.current_value = filtered[0]
            else:
                menu_list.values = [(NO_MATCH, "(no matches)")]
                menu_list.current_value = NO_MATCH
            menu_list._selected_index = 0    # pylint: disable=protected-access
            get_app().invalidate()

        search_field.buffer.on_text_changed += on_text_changed

        # Key bindings: Enter to submit, C-c to cancel
        kb = KeyBindings()

        @kb.add("enter")
        def _key_enter(event):
            if menu_list.values:
                current_selected = menu_list.values[menu_list._selected_index][0]    # pylint: disable=protected-access
                if current_selected is not NO_MATCH:
                    event.app.exit(result=current_selected)
            else:
                event.app.exit(result=None)

        @kb.add("c-c")
        def _key_exit(event):
            event.app.exit(result=None)

        def run_custom_dialog():
            layout = Layout(HSplit([header, search_field, menu_list], height=D()))
            dialog_app = Application(layout=layout, key_bindings=kb, full_screen=True)  # type: ignore
            return dialog_app.run(in_thread=True)

        choice = run_custom_dialog()

        if not choice:
            environment.console.print("\nSelection cancelled.")
            return path

        # A branch node that is a document endpoint and is selected
        if self_endpoint and choice == self_endpoint[0]:
            if action is not None:
                assert path                 # We know path is not empty because self_endpoint defined
                _, current_node = path[-1]  # current_node already defined properly but ... clarity
                action(current_node['filepath'], **kwds)
            return path

        if choice == BACK_LABEL:
            path.pop()
        else:
            current_node = current_data[choice]
            path.append((choice, current_node))

            # A leaf node is always an endpoint, so filepath is not None
            if current_node['subtopics'] is None:
                if action is not None:
                    action(current_node['filepath'], **kwds)
                return path

            current_data = current_node['subtopics']

def menu_select_via_completion(root_data: InfoTree, action: Callable, **kwds) -> list[tuple[str, InfoNode]]:
    """Interactive selection in multi-level menu with completion-dropdown interface.

    Features:
      + Performs fuzzy search of remaining candidates as user types.
      + Allows arrow-key and C-n/C-p navigation of the completion list
      + Includes a Back option at every level
      + Non-leaf loads can be designated as endpoints
      + Executes functions at endpoint nodes with current path as argument

    This is designed for use within a ptpython-based repl.

    The full list is visible before any typing; user types to filter
    it down. A unique fuzzy match can be submitted directly without
    using the navigation keys (arrows or C-n/C-p).

    Parameter ROOT_DATA is a nested dictionary that represents the
    menu structure. Keys are either strings or None, with latter
    indicating that the current node is also a valid endpoint, even
    if it has children. Dictionary values are either child dicts or
    callables or None. A node whose value is callable is an endpoint
    (leaf node), and the callable is invoked with the current 'path'
    (list of keys to that point in the menu) and any keyword-only
    arguments given to this function. A node whose value is
    None is an endpoint (leaf node), and the function returns. A
    node whose value is a dict is a branch node and generates
    another selection at the next level. Any other type of value in
    the dict is ignored and treated as None.

    Returns None if the endpoint is a callable or the leaf node's
    path otherwise.

    """
    path: list[tuple[str, InfoNode]] = []
    current_data: InfoTree = root_data

    while True:
        if not path:
            self_endpoint = []
            base_choices = [k for k in current_data if not k.startswith('_')]
        else:
            current_key, current_node = path[-1]

            # Label for a non-leaf node that is a valid endpoint
            self_endpoint = [f"◉ {current_key}"] if current_node.get('filepath', None) else []

            # Build choice list: self-ref first, then back, then children
            base_choices = (
                self_endpoint
                + [BACK_LABEL]
                + [k for k in current_data if not k.startswith('_')]  # list(current_data)
            )

        # Toolbar: breadcrumb + navigation hint at every level, with color
        hint = f'<ansibrightblack>{NAV_HINT}</ansibrightblack>'
        if not path:
            toolbar = HTML(f'<ansicyan><b>Select a topic</b></ansicyan>   {hint}')
        else:
            breadcrumb = html_escape("  ➔  ".join(p[0] for p in path))
            toolbar = HTML(f'<ansiyellow><b>{breadcrumb}</b></ansiyellow>   │   {hint}')

        completer = FuzzyAllCompleter(base_choices)
        validator = ChoiceValidator(base_choices, allow_empty=self_endpoint is not None)

        def pre_run():
            get_app().current_buffer.start_completion(select_first=False)

        try:
            raw: str = PromptSession().prompt(
                "➔ ",
                completer=completer,
                complete_while_typing=True,
                bottom_toolbar=toolbar,
                validator=validator,
                validate_while_typing=False,
                pre_run=pre_run,
            )
        except (KeyboardInterrupt, EOFError):
            environment.console.print("\nSelection cancelled.")
            return path

        if not raw:  # Empty input
            # We only reach here when self_endpoint is set, so choice is not None
            choice: str | None = self_endpoint[0] if self_endpoint else None
        else:
            choice = match_unique(raw, base_choices)  # non-None guaranteed by validator
        if TYPE_CHECKING:
            assert choice is not None

        if self_endpoint and choice == self_endpoint[0]:
            # Branch node endpoint
            if action is not None:
                assert path                 # We know path is not empty because self_endpoint defined
                _, current_node = path[-1]  # current_node already defined properly but ... clarity
                action(current_node['filepath'], **kwds)
            return path

        if choice == BACK_LABEL:
            path.pop()
        else:
            current_node = current_data[choice]
            path.append((choice, current_node))

            # A leaf node is always an endpoint, so filepath is not None
            if current_node['subtopics'] is None:
                if action is not None:
                    action(current_node['filepath'], **kwds)
                return path

            current_data = current_node['subtopics']


#
# Info Modalities
#

def _flattened_menu(menu: InfoTree, *, key: str, path: list[str]) -> dict[str, InfoNode]:
    flattened = {}
    for k in menu:
        kprime = key + '::' + k.lower() if key else k.lower()
        path.append(k)

        subtree = menu[k]['subtopics']
        if subtree is None:
            flattened[kprime] = menu[k]
        else:
            flattened |= _flattened_menu(subtree, key=kprime, path=path)

        path.pop()
    return flattened

info_tree_joined: dict[str, InfoNode] = _flattened_menu(info_tree, key='', path=[])

def info_interactive(menu: InfoTree, pager=None):
    """Runs the interactive info system for the playground."""
    if environment.info_params.get('dialog', True):
        menu_select_via_dialog(menu, display_info, pager=pager)
    else:
        menu_select_via_completion(menu, display_info, pager=pager)

def info_search(candidate: str, menu: InfoTree, pager=None, flattened=None):
    """Searches for a string multi-level key in info database.

    The search string is a '::' separated string joining keys or
    partial keys at each level. Search is case insensitive.

    If an exact match exists, it is used. If not, a fuzzy
    search is run. If only one matches this way, it is used.
    Otherwise, info_interactive is run with the sub-menu
    containing all candidate matches.

    If no exact or fuzzy matches are found, a descriptive
    message is printed at the terminal.

    """
    # ATTN: preprocess info_tree on first use into joined key lookup
    if flattened is None:
        flattened = _flattened_menu(menu, key='', path=[])

    search_key = candidate.lower()
    if search_key in flattened:
        info_path = flattened[search_key]['filepath']
        if info_path is None:
            print_formatted_text(HTML(f'<violet>Topic {search_key} does not have an associated info document. '
                                      'Try info() to interactively search for related topics.</violet>'))
        else:
            display_info(info_path, pager=pager)
        return

    fuzzies = fuzzy_match(search_key, list(flattened))

    if len(fuzzies) == 0:
        print_formatted_text(HTML(f'<violet>Topic {search_key} does not match any topics. '
                                  'Try info() to interactively search available topics.</violet>'))
        return

    if len(fuzzies) == 1:
        info_path = flattened[fuzzies[0]]['filepath']
        if info_path is None:
            print_formatted_text(HTML(f'<violet>Best matching topic for {search_key} does not have an info document. '
                                      'Try info() to interactively search for related topics.</violet>'))
        else:
            display_info(info_path, pager=pager)
        return

    info_interactive({k: flattened[k] for k in fuzzies}, pager=pager)


#
# Info Display in the Terminal
#

def display_info(docpath: list[str] | None = None, *, obj=None, pager=None) -> None:
    """Displays an info topic document in the repl.

    Parameters
    ----------
    docpath - if supplied, a list of file path components for the document resource
    obj - if supplied, an object whose __info__ attribute will be used to lookup
        the document. The attribute is a ::-separated string of Keys in the info tree.
    pager - if supplied, a Boolean indicating whether to use a pager. If not supplied,
        the environment setting will be used.

    """
    if pager is None:
        pager = environment.info_params.get('pager', False)  # ATTN: Add to environment

    if docpath is None and obj is None:
        docpath = ['_Topics.md']  # Summary of available topics, not typically needed

    if obj is not None:
        if hasattr(obj, '__info__'):
            docpath = obj.__info__.split('::')
            if docpath:
                docpath[-1] += '.md'  # Always a markdown file at the end
        else:
            help(obj)
            return

    if TYPE_CHECKING:
        assert docpath is not None

    topic_path = files('frplib.data') / 'playground-help'
    for d in docpath:
        topic_path = topic_path / d

    if not topic_path.is_file():
        print_formatted_text(HTML('<violet>I could not find any guidance at the specified path. '
                                  'Try info() to interactively search the available topics.</violet>'))
        return

    help_text = topic_path.read_text()
    # ATTN: Rich behaving oddly here
    code_theme = 'monokai' if environment.dark_mode else 'slate'
    info_text = Markdown(help_text, code_theme=code_theme)
    if pager:
        with environment.console.pager():
            environment.console.print(info_text)
    else:
        environment.console.print(info_text)


#
# Info system entry point.  This is the only user-facing function.
#

def info(obj_or_topic=None, pager=None) -> None:
    """Accesses and displays help on a variety of playground topics.

    If obj_or_topic is missing, this engages an interactive search
    interface where topics can be found by hierarchical fuzzy matching
    as the user types.

    If obj_or_topic is a string consisting of ::-separated topic
    keys, this displays an exactly matching topic (with case-insensitive
    comparison) if on exists, or displays a unique topic that matches
    the string in a fuzzy comparison (contains a subsequence of the
    characters of either case). If there are multiple fuzzy matches,
    this engages the interactive system on those combined keys only.
    Unlike the standard interactive system, this search is one
    level only, allowing the user to disambiguate the intended string.

    If obj_or_topic is a Python/frplib object, this looks for the
    __info__ property of the object and uses that to lookup an
    appropriate info document. If not such property is defined,
    this calls help() on the object.

    Finally, if obj_or_topic is a list of strings, the elements
    should represent path components to the corresponding info topic
    document. This last option is is not intended for users.

    If pager is missing (None), the environment setting determines
    pager use, otherwise pager should be a Boolean indicating
    whether a pager should be used to display the info topic
    document, overriding the environment setting.

    """
    if obj_or_topic is None:
        info_interactive(info_tree, pager=pager)
        return

    if isinstance(obj_or_topic, str):
        info_search(obj_or_topic, info_tree, pager=pager, flattened=info_tree_joined)
        # tree: InfoTree | None = info_tree
        # topics = obj_or_topic.split('::')
        # for k in topics[:-1]:
        #     if tree is None:
        #         break
        #
        #     cur: InfoNode | None = tree.get(k, None)
        #     tree = cur.get('subtopics', None) if cur else None
        #
        # target = topics[-1]
        # if not tree or target not in tree or 'filepath' not in tree[target]:
        #     print_formatted_text(HTML(f'<violet>I could not find any guidance on that topic ({obj_or_topic}). '
        #                               'Try info() to interactively search the available topics.</violet>'))
        #     return
        #
        # display_info(tree[target]['filepath'], pager=pager)
    elif isinstance(obj_or_topic, list):
        display_info(docpath=obj_or_topic, pager=pager)
    else:
        display_info(obj=obj_or_topic, pager=pager)


#
# Development Utilities
#

# ATTN
# Might want to make info_tree case insensitive, somewhat like the following:
# If so, put this above and make InfoTree use this in the type.
#
#  class CaseInsensitiveDict(dict):
#      def __init__(self, *args, **kwargs):
#          super().__init__(*args, **kwargs)
#          self._store = {k.lower(): k for k in self.keys()}
#
#      def __getitem__(self, key):
#          return super().__getitem__(self._store[key.lower()])
#
#      # NOTE: ambiguous what x['Foo'] = 2; x['fOo'] = 3; x['foO'] = 4
#        means: original version gives three keys with different values
#               but gets only get the most recent value for all of them
#               this version keeps the original key only, which must
#               be deleted to change, and uses the most recent value
#               for that key and all its iso-spells.
#      def __setitem__(self, key, value):
#          k = key.lower()
#          if k in self._store:
#              self[self._store[k]] = value
#          else:
#              self._store[key.lower()] = key
#              super().__setitem__(key, value)
#
#      def get(self, key, default=None):
#          k = key.lower()
#          if k in self._store:
#              return self[self._store[k]]
#          return default


def _make_info_dict():
    """Creates the info_tree data describing keys and resources for the info system.

    This function is **for development use only**!

    """
    manifest = files('frplib.data') / 'info-manifest.txt'
    data: InfoTree = {}

    current: InfoNode = {'subtopics': None}
    parent: InfoTree = data   # Easy access to parents[-1]
    parents: list[InfoTree] = []

    pattern = re.compile(r'^(?P<indent>(?: {4})*)(?P<key>[^":]+)(?P<desc>"[^"]*")?:[ \t]*(?P<path>.*)$')
    with manifest.open(mode='r', encoding='utf-8') as f:
        for line in f:
            if re.match(r'#', line) or re.match(r'\s*$', line):
                continue

            if (m := re.match(pattern, line)):
                levels = len(parents)
                parsed = m.groupdict()
                level = 1 + (len(parsed['indent']) // 4)
                the_key: str = parsed['key'].rstrip()
                the_path: list[str] = parsed['path'].split()
                the_desc: str = parsed['desc'].replace('"', '') if parsed['desc'] else ''

                if level - levels > 1:
                    if levels == 0:
                        raise ValueError('First line of info manifest file should have zero indent')
                    raise ValueError(f'Sub-topic indented from parent by more than one level: {line}')

                subtopic: InfoNode = {'subtopics': None}
                if the_path:
                    subtopic['filepath'] = the_path
                if the_desc:
                    subtopic['description'] = the_desc

                if levels == 0 and level == 1:  # Initial setup, first step from root
                    parent[the_key] = subtopic
                    parents.append(parent)
                    current = subtopic
                elif level == levels:
                    parent[the_key] = subtopic
                    current = subtopic
                elif level > levels:   # Differ by 1 by above check
                    if (super_tree := current['subtopics']) is None:   # This rigamarole is for mypy
                        super_tree = cast(InfoTree, {})
                        current['subtopics'] = super_tree
                    super_tree[the_key] = subtopic
                    parent_subtopic = super_tree

                    parent = parent_subtopic
                    parents.append(parent_subtopic)
                    current = subtopic
                elif level < levels:
                    diff = levels - level
                    for _ in range(diff):
                        parents.pop()
                    parent = parents[-1]
                    parent[the_key] = subtopic
                    current = subtopic
            else:
                raise ValueError(f'Improper syntax for info manifest line: {line}')

    return data

# Executing with uv run will produce a new version of info_tree.py

if __name__ == '__main__':
    import pprint
    import subprocess
    import sys

    it = _make_info_dict()
    tree_rs = files('frplib.data') / 'info_tree.py'

    with as_file(tree_rs) as physical_path:
        with physical_path.open("w", encoding='utf-8') as f:
            print(f"Generating {str(physical_path)}...", end='', flush=True)
            print('"""Generated file defining the dictionary representing the info topic document tree."""',
                  file=f)
            print("\nfrom frplib.repls.info_types import InfoTree\n", file=f)
            print("info_tree: InfoTree = ", file=f, end='')
            pprint.pp(it, stream=f, indent=4, width=100)

        print(" formatting...", end='', flush=True)
        subprocess.run([sys.executable, '-m', 'black', '-q', str(physical_path)], check=True)
        print("Done")
