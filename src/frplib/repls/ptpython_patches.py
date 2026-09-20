"""Monkeypatch for ptpython's Jedi-based signature/docstring popup.

  Background
  ----------

  ptpython's inline signature toolbar and docstring pane both display
  whichever signature ends up first in python_input.signatures (see
  ptpython.layout.signature_toolbar, and python_input.py's
  docstring_buffer.reset(document=Document(signatures[0].docstring, ...))).
  That list is built by ptpython.python_input.get_signatures_using_jedi,
  which frplib's playground_repl never calls directly. It is read at
  call time out of the ptpython.python_input module namespace, which is
  what makes patching it there (rather than in ptpython.signatures, where
  it's originally defined) actually effective; see the note on the
  patch target below.

  For a callable *instance* that wraps a real function this produces
  an incorrect display in two distinct ways. The motivating use
  case are factories built with frplib's Factory/KindFactory/etc.
  from factories.py. These factories have a docstring built from
  the original object.

  1. Static, source-based analysis (jedi.Script) resolves *two*
     candidates for a call like `uniform(`: a generic one from the
     wrapper class's own __call__ ("KindFactory(*args, **kwds)"),
     and a specific one traced through to the real wrapped function
     ("uniform(*xs: ...) -> Kind"), in that order -- so simply
     taking signatures[0] picks the wrong one.

     However, ptpython does NOT use jedi.Script for live REPL typing. It
     uses jedi.Interpreter (see get_jedi_script_from_document).
     The latter reflects on the actual runtime object already bound in the
     session's namespace rather than tracing source. In practice,
     this returns exactly one generic candidate. As a result, this
     step does not have any effect. It's kept here for the moment
     in case a future jedi/ptpython combination ever does return
     multiple candidates in Interpreter mode too. This might
     be eliminated.

  2. In Interpreter mode, Jedi's single candidate already has the *correct*
     parameters and docstring content. It follows the __wrapped__ chain
     correctly, but when Jedi creates a "name(params)\n\ndocstring",
     it still uses the wrapper class's name (e.g., KindFactory),
     not the instance's own __name__. This suggests that name resolution
     is independent of the parameter/docstring introspection.

     ptpython also has its own fallback for when Jedi finds nothing
     -- get_signatures_using_eval. This resolves the callable by
     evaluating the expression text directly and reading
     obj.__name__ / inspect.signature(obj) / obj.__doc__ off the
     real object. This search correctly follows __wrapped__ for
     these wrapper objects. So: when jedi's top candidate is a
     generic instance-__call__ resolution, this patch calls
     get_signatures_using_eval itself and substitutes its result for
     that candidate specifically.

     That fixes the name and parameters, but introduces a second,
     smaller wrinkle: get_signatures_using_eval's docstring is plain
     obj.__doc__, which for a Factory instance is the "friendly" factory
     description (see factories.py) with *no* signature line at all --
     unlike jedi's own (mis-named) candidate, which had one. To restore
     the correct name, this patch does a
     best-effort plain-name lookup of the resolved object in
     locals/globals. If found, this rebuilds the docstring
     with the correct name and signature and an appropriate choice
     of the docstring. The goal is for this help (rather than info, say)
     to give "developer-friendly" documentation. This lookup only
     handles a simple bound name, not arbitrary expressions the way
     get_signatures_using_eval itself does,. This covers frplib's
     motivating need, with Factory objects,  and silently
     falls back to get_signatures_using_eval's own docstring otherwise.
     It does leave a gap for more general wrapped object that might
     prove significant.

     Known simplification: unlike ptpython's own use of
     get_signatures_using_eval (which checks self.enable_dictionary_completion
     before calling it), this patch calls it unconditionally in the
     generic-instance case, since the function signature here
     (document, locals, globals) has no access to the PythonInput
     instance to check that flag. Evaluating the expression text has
     the same characteristics as ptpython's own existing fallback use of
     this function (e.g. a compound expression before the open paren
     could itself invoke other calls). This patch doesn't introduce
     additional risk, just one more circumstance that might trigger
     something ptpython already does elsewhere.

  This patches ptpython.python_input.get_signatures_using_jedi, the
  name actually referenced by ptpython's input-handling code. Note
  that patching ptpython.signatures.get_signatures_using_jedi
  instead would have no effect because python_input.py imports the
  name directly into its own namespace.

  This patch is nice to have but is ultimately cosmetic and as such
  low priority. The key rule is to never cause a problem in the playground,
  so if any of ptpython's internals show a mismatch or problem,
  the patch will silently decline to apply.

  We use this in playground.py as:

  from frplib.repls.ptpython_patches import apply_signature_display_patch

  def configure(repl):
      ...
      apply_signature_display_patch()
      ...

  apply_signature_display_patch() returns a bool so we can check
  (and possibly log, e.g. only under a debug env var) what happened
  we can log something diagnostic at the call site if desired ().

"""
# pylint: disable=broad-exception-caught, pointless-statement, redefined-builtin

from __future__ import annotations

import inspect

from frplib.factories import Factory


_PREFERRED_JEDI_TYPES = frozenset({'function', 'bound_method', 'method', 'compiled_function'})

# Set of Jedi .type values that indicate "some object's __call__ is being invoked".
# The motivation for this patch is where the name on the object is wrong,
# e.g., KindFactory rather than the factory name. The signature is generally
# correct. In that case, we have observed 'instance' for the .type.
# It's possible that 'class' should be here too, but that has not yet been
# confirmed with evidence, so it is excluded for now.
_GENERIC_CALL_TYPES = frozenset({'instance'})

# Versions of ptpython for which this patch has been tested.
# Because of dependencies with ptpython internals in the playground repl,
# the ptpython version is pinned to a specific version in pyproject.toml.
# That version should belong to this set, though others might also
# be included for information. If the pin is ever loosened, this check
# prevents the patch from applying when the version is untested.
_TESTED_PTPYTHON_VERSIONS = {'3.0.32'}

def apply_signature_display_patch() -> bool:
    """Fixes ptpython's Jedi-based signature/docstring popup for wrapped objects.

    Returns True if the patch was applied, False if it was skipped.
    The latter will occur if the current version of ptpython's internals
    do not match what this expects. This will not raise an error.
    It is a low priority enhancement and is silently skipped if any
    problems are encountered.

    """
    try:
        import importlib.metadata
        if importlib.metadata.version('ptpython') not in _TESTED_PTPYTHON_VERSIONS:
            return False

        import ptpython.python_input as _pi
        from ptpython.signatures import Signature as _PTSignature
        from ptpython.signatures import get_signatures_using_eval as _get_signatures_using_eval
        from ptpython.utils      import get_jedi_script_from_document

        if not hasattr(_pi, 'get_signatures_using_jedi'):
            return False
        if not hasattr(_PTSignature, 'from_jedi_signature'):
            return False

        def _patched_get_signatures_using_jedi(document, locals, globals):
            script = get_jedi_script_from_document(document, locals, globals)
            if not script:
                return []
            try:
                raw_sigs = script.get_signatures()
            except Exception:
                raw_sigs = []
            else:
                try:
                    if raw_sigs:
                        raw_sigs[0].params
                except AttributeError:
                    pass

            # Step 1: Order the signatures with preferred types first.
            # This currently has no effect because jedi.Interpreter only
            # ever returns one candidate for a __call__-resolved instance.
            # This is harmles to keep for the moment but provides a useful
            # possibility looking forward.
            try:
                raw_sigs = sorted(
                    raw_sigs,
                    key=lambda s: 0 if getattr(s, 'type', None) in _PREFERRED_JEDI_TYPES else 1,
                )
            except Exception:
                pass  # fall back to default ordering if the above fails for any reason

            signatures = [_PTSignature.from_jedi_signature(sig) for sig in raw_sigs]

            # Step 2: search for the desired signature
            if signatures and getattr(raw_sigs[0], 'type', None) in _GENERIC_CALL_TYPES:
                try:
                    eval_sigs = _get_signatures_using_eval(document, locals, globals)
                except Exception:
                    eval_sigs = []
                if eval_sigs:
                    # get_signatures_using_eval already gets the name and
                    # parameters right (both follow __wrapped__ correctly),
                    # but its docstring is plain obj.__doc__ -- for a Factory
                    # instance, that's the "friendly" factory description
                    # (see factories.py), with no signature line at all. Best-
                    # effort rebuild it the same way help.py's forced-builtin
                    # path does: unwrap to the real function and use *its*
                    # docstring, prefixed with the (correctly named) signature
                    # line, for a consistent "developer-friendly" presentation
                    # in both places. Only a plain-name lookup is attempted
                    # here (not the full expression eval get_signatures_using_eval
                    # itself does), so this is skipped -- falling back to
                    # get_signatures_using_eval's own docstring -- for anything
                    # other than a simple bound name, which covers frplib's
                    # actual usage pattern (Factory objects as top-level names).
                    top = eval_sigs[0]
                    obj = (locals or {}).get(top.name, (globals or {}).get(top.name))
                    if obj is not None:
                        try:
                            if isinstance(obj, Factory):
                                # NOTE: For the cases we care about (Factories), we want the docstring
                                # from the wrapper object but the name from the wrapped object.
                                # The former has been built from the wrapped object's docstring
                                # so is actually nicer.
                                real_doc = inspect.getdoc(obj) or ''
                            else:
                                # For a general wrapped object, we will use the unwrapped
                                # object's docstring. We will have to see if this is
                                # the desired behavior in general.
                                real_doc = inspect.getdoc(inspect.unwrap(obj)) or ''
                            top.docstring = f'{top.name}{inspect.signature(obj)}\n\n{real_doc}'.rstrip()
                        except Exception:
                            pass  # use the original singnatures if the search fails
                    signatures = eval_sigs + signatures[1:]

            return signatures

        _pi.get_signatures_using_jedi = _patched_get_signatures_using_jedi
        return True

    except Exception:
        return False
