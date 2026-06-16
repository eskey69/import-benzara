from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from import_benzara.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["generate-latest-stock-feed", *sys.argv[1:]]))
