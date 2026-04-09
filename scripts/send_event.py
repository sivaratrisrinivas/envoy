from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig


SCENARIOS = {
    "hero_job_change": {
        "event_id": "evt_hero_001",
        "event_type": "job_change",
        "occurred_at": "2026-04-09T10:00:00Z",
        "confidence": 0.95,
        "confidence_reason": "confirmed_role_change",
        "person_name": "Priya Nair",
        "person_linkedin_url": "https://linkedin.com/in/priyanair",
        "old_company_name": "Northstar Cloud",
        "old_company_domain": "northstar.example",
        "new_company_name": "Acme Frontier",
        "new_company_domain": "acmefrontier.example",
        "new_title": "VP Revenue Operations",
        "trigger_reason": "Known champion moved to a net-new target account",
        "crm_lookup_keys": {
            "linkedin_url": "https://linkedin.com/in/priyanair",
            "old_company_domain": "northstar.example",
            "new_company_domain": "acmefrontier.example",
        },
        "source_payload": {"provider": "crustdata-like", "event": "job_change"},
    },
    "backup_job_change": {
        "event_id": "evt_backup_001",
        "event_type": "job_change",
        "occurred_at": "2026-04-09T11:00:00Z",
        "confidence": 0.91,
        "confidence_reason": "confirmed_role_change",
        "person_name": "Alex Chen",
        "person_linkedin_url": "https://linkedin.com/in/alexchen",
        "old_company_name": "Pioneer Metrics",
        "old_company_domain": "pioneermetrics.example",
        "new_company_name": "Orbit Forge",
        "new_company_domain": "orbitforge.example",
        "new_title": "Head of Revenue Systems",
        "trigger_reason": "Backup scenario for champion move",
        "crm_lookup_keys": {
            "linkedin_url": "https://linkedin.com/in/alexchen",
            "old_company_domain": "pioneermetrics.example",
            "new_company_domain": "orbitforge.example",
        },
        "source_payload": {"provider": "crustdata-like", "event": "job_change"},
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=sorted(SCENARIOS))
    parser.add_argument("--server", default="http://localhost:8000")
    parser.add_argument("--secret")
    parser.add_argument("--event-id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = AppConfig.from_env()
    payload = dict(SCENARIOS[args.scenario])
    if args.event_id:
        payload["event_id"] = args.event_id

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return

    endpoint = args.server.rstrip("/") + "/webhook/crustdata"
    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Secret": args.secret or config.webhook_secret,
        },
        method="POST",
    )
    with request.urlopen(req) as response:
        print(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
