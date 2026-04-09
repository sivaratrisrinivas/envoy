from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig
from app.crm.airtable import AirtableCRMClient
from app.crm.fake import FakeCRMClient


def main() -> None:
    config = AppConfig.from_env()
    if config.crm_mode == "airtable":
        client = AirtableCRMClient(config)
        client.seed_demo()
        print("Seeded Airtable demo namespace")
        return

    client = FakeCRMClient(config)
    client.save_state(
        {
            "contacts": {
                "https://linkedin.com/in/priyanair": {
                    "full_name": "Priya Nair",
                    "linkedin_url": "https://linkedin.com/in/priyanair",
                    "current_account": "Northstar Cloud",
                    "former_account": "Southwind Analytics",
                    "ae_owner": "Jordan Lee",
                    "relationship_memory": "Priya previously evaluated pipeline tooling with Jordan while at Northstar Cloud.",
                    "last_meeting_note": "Discussed revops visibility and handoff friction between SDR and AE teams.",
                    "previous_opportunity_context": "Open evaluation at prior company did not close due to timing.",
                    "talking_points": ["reconnect after role change", "offer relevant revops insight"],
                }
            },
            "accounts": {
                "northstar.example": {
                    "account_name": "Northstar Cloud",
                    "domain": "northstar.example",
                    "status": "active",
                }
            },
            "activity_log": {},
        }
    )
    print(f"Seeded fake CRM at {config.fake_crm_path}")


if __name__ == "__main__":
    main()
