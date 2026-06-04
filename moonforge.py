#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

# Handle running uninstalled
moonforge_bin = Path(sys.argv[0]).resolve()
if (moonforge_bin.parent / 'src' / 'moonforgecli').is_dir():
    sys.path.insert(0, str(moonforge_bin.parent / 'src'))


if __name__ == '__main__':
    from moonforgecli import moonforgemain

    """Main entry point. Instantiates the moonforge application and runs it."""
    if sys.version_info < (3, 10):  # pragma: no cover
        print(f"moonforge requires Python >= 3.10, but you have version {sys.version_info}")
        print("Please update your environment to use moonforge")
        sys.exit(1)
    app = moonforgemain.MoonforgeApp()
    sys.exit(app.run(sys.argv[1:]))
