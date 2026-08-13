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
        src = os.path.join(self.root, 'src')
        env = dict(os.environ, PYTHONPATH=src)
        subprocess.run(
            [sys.executable, '-m', 'frplib.repls.info'],
            check=True, cwd=self.root, env=env,
        )
