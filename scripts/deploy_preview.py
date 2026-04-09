from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    railway = shutil.which("railway")
    if railway is None:
        raise SystemExit("railway CLI is not installed or not on PATH")
    subprocess.run([railway, "up", "--detach", "-m", "preview deploy"], check=True)


if __name__ == "__main__":
    main()
