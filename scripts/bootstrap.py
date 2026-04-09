from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig
from app.runtime import AppRuntime


def main() -> None:
    config = AppConfig.from_env()
    AppRuntime.build(config)
    print(f"Bootstrapped local state at {config.local_dir}")


if __name__ == "__main__":
    main()
