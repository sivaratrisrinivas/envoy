from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig
from app.crm.airtable import AirtableCRMClient
from app.storage import ControlPlaneStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args()
    if args.confirm != "preview":
        raise SystemExit("refusing to reset preview without --confirm preview")

    config = AppConfig.from_env()
    ControlPlaneStore(config).reset_namespace()
    if config.crm_mode == "airtable":
        AirtableCRMClient(config).reset_demo_namespace()
        print(f"Reset preview namespace for {config.tenant_id}/{config.demo_env}")
        return
    if config.fake_crm_path.exists():
        config.fake_crm_path.unlink()
    print(f"Reset local preview-style state for {config.tenant_id}/{config.demo_env}")



if __name__ == "__main__":
    main()
