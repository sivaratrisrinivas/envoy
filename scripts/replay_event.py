from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig
from app.runtime import AppRuntime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("event_id")
    args = parser.parse_args()

    runtime = AppRuntime.build(AppConfig.from_env())
    runtime.replay_event(args.event_id)
    print(f"Replayed {args.event_id}")


if __name__ == "__main__":
    main()
