"""Blog-Junction für Quarto-Preview: presentation/Blog -> ../Blog."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINK = HERE / "Blog"
TARGET = (HERE / ".." / "Blog").resolve()


def main() -> int:
    if not TARGET.is_dir():
        print(f"Blog-Quelle fehlt: {TARGET}", file=sys.stderr)
        return 1
    if LINK.exists():
        return 0
    if sys.platform == "win32":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(LINK), str(TARGET)],
            check=True,
        )
    else:
        LINK.symlink_to(TARGET, target_is_directory=True)
    print(f"Linked {LINK} -> {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
