#!/usr/bin/env python3
"""Checks frplib's ptpython integration for two ptpython versions.

Background
----------

frplib's PlaygroundRepl (src/frplib/repls/playground_repl.py) subclasses
ptpython's PythonRepl and overrides six underscore-prefixed (explicitly
private, no-stability-guarantee) methods:

    _compile_with_flags, _show_result, _handle_exception,
    _handle_keyboard_interrupt, _add_to_namespace, _remove_from_namespace

Some of the overrides also
implicitly depend on the *behavior* of what they call through to, not
just its name existing:

    - _show_result's non-Renderable branch calls super()._show_result(...).
    - _handle_exception super()._handle_exception(e) indirectly, via
      _show_exception_trimmed() for  anything that
      is not an FrplibException or IndexError/KeyError. This also
      temporarily swaps e.__traceback__ to a trimmed version, but this
      only works if  super()._handle_exception reads the traceback off
      e.__traceback__  rather than capturing it independently (e.g. via sys.exc_info()),
      which it currently does.
    - _show_result's own docstring notes that blank-line handling around
      the printed result is done by run_and_show_expression() *after*
      _show_result returns -- a coupling to that caller's specific
      behavior, not just _show_result's own.

frplib also depends on the public-facing get_compiler_flags() and the
current_statement_index attribute. (The latter is also used by ptpython's own
prompt styles, so represents low risk. But that is not fully documented
in the public API).

In addition, src/frplib/repls/ptpython_patches.py monkeypatches
ptpython.python_input.get_signatures_using_jedi to adjust the docstring
popups in the playground, especially for Factory objects, to show the
correct name and signature. However, that change is independently
version-gated (see _TESTED_PTPYTHON_VERSIONS there).

Because these are internal methods and non-public behaviors,
they can change in any way (including disappearing) between
ptpython versions, even a patch release. This would not be documented
as a breaking change. So, we need a procedure for checking before
updgrading the ptpython version that is pinned by frplib.

The full manual procedure checking a ptpython upgrade is:

  1. Check for a new release (e.g. against the pin in pyproject.toml):
         curl -s https://pypi.org/pypi/ptpython/json \
             | python3 -c "import json,sys; print(json.load(sys.stdin)['info']['version'])"

  2. Install the candidate version into an isolated env, not yet touching
     the pinned version:

         python3 -m venv /tmp/ptpython_check
         source /tmp/ptpython_check/bin/activate
         pip install "ptpython==<candidate>" jedi

  3. Structural check: do the tracked names still exist, with matching
     signatures? This is one step handled by THIS SCRIPT.

  4. Behavioral check: did the *source* of the methods frplib's
     overrides implicitly depend on (via super() calls or documented
     coupling) actually change?  This is one step handled by THIS SCRIPT.

  5. Re-run the ptpython_patches.py verification suite (see the checks
     built for apply_signature_ordering_patch()) against the candidate
     version, and add it to _TESTED_PTPYTHON_VERSIONS once confirmed.

  6. Live test: actually launch the playground under the candidate
     version and manually exercise what static checking can't cover:
     a Renderable result display, a triggered IndexError/KeyError, a
     generic exception (check the trimmed traceback and explain_error()),
     Ctrl-C, and namespace injection (environment, info, help, cookbook,
     etc. all present).

  7. Only then bump the pin in pyproject.toml, updating
     _TESTED_PTPYTHON_VERSIONS in ptpython_patches.py at the same
     time.

This script automates steps 3 and 4 only. Steps 1, 2, 5, 6, and 7 are
still require manual intervention.

Usage
-----
Run this script like

    python scripts/check_ptpython_compat.py <python1> <python2>

where <python1> and <python2> are paths to Python executables in two
environments with (potentially different) ptpython versions
installed. This will typically be the project's normal .venv (the
currently pinned version) and a scratch venv holding the candidate
version from step 2 above. For instance, in the project directory:

    python scripts/check_ptpython_compat.py .venv/bin/python /path/to/scratch/venv/bin/python

Each is invoked as a subprocess to collect its own snapshot, so both
versions never need to be importable in the same process.

Exit status is 0 if nothing tracked differs, 1 if anything is missing,
changed, or errored.

"""

from __future__ import annotations

import difflib
import json
import subprocess
import sys

# Methods checked by signature only: do they still exist, with the same
# parameters? All looked up on ptpython.repl.PythonRepl.

TRACKED_SIGNATURES = [
    '_compile_with_flags',
    '_show_result',
    '_handle_exception',
    '_handle_keyboard_interrupt',
    '_add_to_namespace',
    '_remove_from_namespace',
    'get_compiler_flags',
]

# Methods checked by full source diff: frplib's overrides depend on their
# *behavior*, not just their name/signature, via a super() call or a
# documented coupling.

TRACKED_SOURCES = [
    '_show_result',
    '_handle_exception',
    'run_and_show_expression',
    'run_and_show_expression_async',
]

# Attributes checked by presence only (not real methods, so no signature
# to compare). Just confirm that the name is still referenced somewhere in
# ptpython's own relevant modules.

TRACKED_ATTRS = ['current_statement_index']

_ATTR_SEARCH_MODULES = ['ptpython.repl', 'ptpython.python_input', 'ptpython.prompt_style']


def _collect_snapshot() -> dict:
    """Collects the tracked ptpython surface from *this* Python environment."""
    import importlib
    import importlib.metadata
    import inspect

    snapshot: dict = {'version': None, 'signatures': {}, 'sources': {}, 'attrs': {}}

    try:
        snapshot['version'] = importlib.metadata.version('ptpython')
        from ptpython.repl import PythonRepl
    except Exception as e:                    # pylint: disable=broad-exception-caught
        return {'error': f'{type(e).__name__}: {e}'}

    for name in TRACKED_SIGNATURES:
        method = getattr(PythonRepl, name, None)
        snapshot['signatures'][name] = str(inspect.signature(method)) if method is not None else None

    for name in TRACKED_SOURCES:
        method = getattr(PythonRepl, name, None)
        try:
            snapshot['sources'][name] = inspect.getsource(method) if method is not None else None
        except (OSError, TypeError):
            snapshot['sources'][name] = None

    combined_source = ''
    for modname in _ATTR_SEARCH_MODULES:
        try:
            mod = importlib.import_module(modname)
            combined_source += inspect.getsource(mod)
        except Exception:                     # pylint: disable=broad-exception-caught
            pass
    for name in TRACKED_ATTRS:
        snapshot['attrs'][name] = name in combined_source

    return snapshot


def _dump_and_exit() -> None:
    print(json.dumps(_collect_snapshot()))
    sys.exit(0)


def _snapshot_from(python_exe: str) -> dict:
    result = subprocess.run(
        [python_exe, __file__, '--dump'],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return {'error': f'Could not run under {python_exe!r}: {result.stderr.strip()}'}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {'error': f'Could not parse output from {python_exe!r}: {e}'}


def _report(python1: str, python2: str, snap1: dict, snap2: dict) -> bool:
    """Prints a comparison report. Returns True if everything matches."""
    ok = True

    if 'error' in snap1:
        print(f'{python1}: {snap1["error"]}')
        return False
    if 'error' in snap2:
        print(f'{python2}: {snap2["error"]}')
        return False

    print(f'Comparing ptpython {snap1["version"]} ({python1})')
    print(f'      against ptpython {snap2["version"]} ({python2})\n')

    print('-- Signatures --')
    for name in TRACKED_SIGNATURES:
        sig1, sig2 = snap1['signatures'].get(name), snap2['signatures'].get(name)
        if sig1 is None or sig2 is None:
            print(f'  MISSING  {name}: {sig1!r} -> {sig2!r}')
            ok = False
        elif sig1 != sig2:
            print(f'  CHANGED  {name}:')
            print(f'      old: {sig1}')
            print(f'      new: {sig2}')
            ok = False
        else:
            print(f'  ok       {name}')

    print('\n-- Attributes --')
    for name in TRACKED_ATTRS:
        present1, present2 = snap1['attrs'].get(name), snap2['attrs'].get(name)
        if not present1 or not present2:
            print(f'  MISSING  {name}: found_in_old={present1} found_in_new={present2}')
            ok = False
        else:
            print(f'  ok       {name}')

    print('\n-- Source (behavioral) --')
    for name in TRACKED_SOURCES:
        src1, src2 = snap1['sources'].get(name), snap2['sources'].get(name)
        if src1 is None or src2 is None:
            print(f'  MISSING  {name}')
            ok = False
        elif src1 != src2:
            print(f'  CHANGED  {name}:')
            diff = difflib.unified_diff(
                src1.splitlines(keepends=True), src2.splitlines(keepends=True),
                fromfile=f'{name} (old)', tofile=f'{name} (new)',
            )
            for line in diff:
                print('      ' + line.rstrip('\n'))
            ok = False
        else:
            print(f'  ok       {name} (unchanged)')

    print()
    print('PASS -- nothing tracked has changed.' if ok else
          'REVIEW NEEDED -- see flagged items above (manual steps 4-6 still apply regardless).')
    return ok


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == '--dump':
        _dump_and_exit()

    if len(sys.argv) != 3:
        print(__doc__)
        print(f'Usage: {sys.argv[0]} <python1> <python2>', file=sys.stderr)
        sys.exit(2)

    python1, python2 = sys.argv[1], sys.argv[2]
    snap1 = _snapshot_from(python1)
    snap2 = _snapshot_from(python2)
    ok = _report(python1, python2, snap1, snap2)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
