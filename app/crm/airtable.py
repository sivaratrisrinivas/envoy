from __future__ import annotations

from typing import Any

import httpx

from app.config import AppConfig
from app.models import DraftArtifact, JobChangeEvent


class AirtableCRMClient:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        if not config.airtable_api_key or not config.airtable_base_id:
            raise ValueError("Airtable configuration is incomplete")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.airtable_api_key}",
            "Content-Type": "application/json",
        }

    def _table_url(self, table_name: str) -> str:
        return f"https://api.airtable.com/v0/{self.config.airtable_base_id}/{table_name}"

    def _list_records(self, table_name: str, formula: str) -> list[dict[str, Any]]:
        response = httpx.get(
            self._table_url(table_name),
            headers=self._headers(),
            params={"filterByFormula": formula},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json().get("records", [])

    def load_contact_context(self, linkedin_url: str) -> dict[str, Any]:
        records = self._list_records(self.config.airtable_contacts_table, f"{{linkedin_url}} = '{linkedin_url}'")
        if not records:
            return {}
        return records[0]["fields"]

    def apply_job_change(self, event: JobChangeEvent, draft: DraftArtifact) -> None:
        account_fields = {
            "account_name": event.new_company_name,
            "domain": event.new_company_domain,
            "status": "watchlist_generated",
            "last_signal_type": event.event_type,
            "last_signal_at": event.occurred_at,
            "demo_env": self.config.demo_env,
        }
        httpx.post(
            self._table_url(self.config.airtable_accounts_table),
            headers=self._headers(),
            json={"records": [{"fields": account_fields}], "typecast": True},
            timeout=10.0,
        ).raise_for_status()

        contact_fields = {
            "full_name": event.person_name,
            "linkedin_url": event.person_linkedin_url,
            "email": event.email,
            "current_title": event.new_title,
            "current_account": event.new_company_name,
            "former_account": event.old_company_name,
            "status": "moved_recently",
            "draft_subject": draft.subject,
            "draft_body": draft.body,
            "draft_preview": draft.body.splitlines()[0],
            "draft_status": "draft_ready",
            "draft_generated_at": event.occurred_at,
            "draft_event_id": event.event_id,
            "last_event_id": event.event_id,
            "demo_env": self.config.demo_env,
        }
        httpx.post(
            self._table_url(self.config.airtable_contacts_table),
            headers=self._headers(),
            json={"records": [{"fields": contact_fields}], "typecast": True},
            timeout=10.0,
        ).raise_for_status()

        activity_fields = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "contact": event.person_name,
            "from_account": event.old_company_name,
            "to_account": event.new_company_name,
            "status": "draft_ready",
            "summary": f"{event.person_name} moved from {event.old_company_name} to {event.new_company_name}.",
            "rep_note": f"Known champion moved to net-new account {event.new_company_name}; reconnect draft prepared.",
            "email_excerpt": draft.body[:180],
            "created_at": event.occurred_at,
            "updated_at": event.occurred_at,
            "demo_env": self.config.demo_env,
        }
        httpx.post(
            self._table_url(self.config.airtable_activity_table),
            headers=self._headers(),
            json={"records": [{"fields": activity_fields}], "typecast": True},
            timeout=10.0,
        ).raise_for_status()

    def seed_demo(self) -> None:
        records = [
            {
                "fields": {
                    "full_name": "Priya Nair",
                    "linkedin_url": "https://linkedin.com/in/priyanair",
                    "current_account": "Northstar Cloud",
                    "former_account": "Southwind Analytics",
                    "ae_owner": "Jordan Lee",
                    "relationship_memory": "Priya previously evaluated pipeline tooling with Jordan while at Northstar Cloud.",
                    "last_meeting_note": "Discussed revops visibility and handoff friction between SDR and AE teams.",
                    "previous_opportunity_context": "Open evaluation at prior company did not close due to timing.",
                    "demo_env": self.config.demo_env,
                }
            }
        ]
        httpx.post(
            self._table_url(self.config.airtable_contacts_table),
            headers=self._headers(),
            json={"records": records, "typecast": True},
            timeout=10.0,
        ).raise_for_status()
        httpx.post(
            self._table_url(self.config.airtable_accounts_table),
            headers=self._headers(),
            json={
                "records": [
                    {
                        "fields": {
                            "account_name": "Northstar Cloud",
                            "domain": "northstar.example",
                            "status": "active",
                            "demo_env": self.config.demo_env,
                        }
                    }
                ],
                "typecast": True,
            },
            timeout=10.0,
        ).raise_for_status()

    def reset_demo_namespace(self) -> None:
        formula = f"{{demo_env}} = '{self.config.demo_env}'"
        for table_name in [
            self.config.airtable_activity_table,
            self.config.airtable_contacts_table,
            self.config.airtable_accounts_table,
        ]:
            records = self._list_records(table_name, formula)
            if not records:
                continue
            ids = [record["id"] for record in records]
            httpx.delete(
                self._table_url(table_name),
                headers=self._headers(),
                params=[("records[]", record_id) for record_id in ids],
                timeout=10.0,
            ).raise_for_status()
