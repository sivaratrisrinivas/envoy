from __future__ import annotations

import json
from typing import Any

from app.config import AppConfig
from app.models import DraftArtifact, JobChangeEvent


class FakeCRMClient:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.config.ensure_directories()

    def load_state(self) -> dict[str, Any]:
        if not self.config.fake_crm_path.exists():
            return {
                "contacts": {},
                "accounts": {},
                "activity_log": {},
            }
        return json.loads(self.config.fake_crm_path.read_text())

    def save_state(self, state: dict[str, Any]) -> None:
        self.config.fake_crm_path.write_text(json.dumps(state, indent=2, sort_keys=True))

    def load_contact_context(self, linkedin_url: str) -> dict[str, Any]:
        state = self.load_state()
        return state["contacts"].get(linkedin_url, {})

    def apply_job_change(self, event: JobChangeEvent, draft: DraftArtifact) -> None:
        state = self.load_state()

        contacts = state["contacts"]
        accounts = state["accounts"]
        activity_log = state["activity_log"]

        accounts[event.new_company_domain] = {
            "account_name": event.new_company_name,
            "domain": event.new_company_domain,
            "status": "watchlist_generated",
            "last_signal_type": event.event_type,
            "last_signal_at": event.occurred_at,
        }

        contact_key = event.person_linkedin_url
        existing_contact = contacts.get(contact_key, {})
        contacts[contact_key] = {
            "full_name": event.person_name,
            "linkedin_url": event.person_linkedin_url,
            "email": event.email,
            "current_title": event.new_title,
            "current_account": event.new_company_name,
            "former_account": event.old_company_name,
            "status": "moved_recently",
            "outreach_readiness": "ready" if event.email else "draft_ready_no_email",
            "draft_subject": draft.subject,
            "draft_body": draft.body,
            "draft_preview": draft.body.splitlines()[0],
            "draft_status": "draft_ready",
            "draft_generated_at": event.occurred_at,
            "draft_event_id": event.event_id,
            "last_event_id": event.event_id,
            "ae_owner": existing_contact.get("ae_owner", "Jordan Lee"),
            "relationship_memory": existing_contact.get(
                "relationship_memory",
                "Priya previously evaluated pipeline tooling with Jordan while at Northstar Cloud.",
            ),
            "last_meeting_note": existing_contact.get(
                "last_meeting_note",
                "Discussed revops visibility and handoff friction between SDR and AE teams.",
            ),
            "previous_opportunity_context": existing_contact.get(
                "previous_opportunity_context",
                "Open evaluation at prior company did not close due to timing.",
            ),
            "talking_points": existing_contact.get(
                "talking_points",
                ["reconnect after role change", "offer relevant revops insight"],
            ),
        }

        activity_log[event.event_id] = {
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
        }

        self.save_state(state)
