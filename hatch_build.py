"""Hatchling build hook that regenerates frplib/data/info_tree.py at build time.

info_tree.py is derived from info-manifest.txt and is gitignored (not tracked
in version control, see the `info-tree` Makefile target for local/dev use),
so a wheel/sdist build must (re)generate it -- otherwise anything installed
from that built artifact would be missing the file entirely.

"""

import os
import subprocess
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class InfoTreeBuildHook(BuildHookInterface):
    PLUGIN_NAME = 'info-tree'

    def initialize(self, version, build_data):
        # Forward this process's own site-packages dirs (not just PYTHONPATH)
        # to the subprocess: pip's build isolation makes declared build
        # dependencies importable here via an in-memory sys.path overlay,
        # which a freshly spawned subprocess would not otherwise inherit.
        # Only the site-packages entries are forwarded, not all of sys.path:
        # pip's isolation also adds its own bootstrap "site" dir carrying a
        # sitecustomize.py that asserts an invocation context that doesn't
        # hold for a plain subprocess, raising AssertionError if imported here.
        src = os.path.join(self.root, 'src')
        site_packages_dirs = [p for p in sys.path if 'site-packages' in p]
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join([src, *site_packages_dirs])
        subprocess.run(
            [sys.executable, '-m', 'frplib.repls.info'],
            check=True, cwd=self.root, env=env,
        )
