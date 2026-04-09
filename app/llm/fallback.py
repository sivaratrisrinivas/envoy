from __future__ import annotations

from app.config import AppConfig
from app.models import DraftArtifact, JobChangeEvent


def generate_fallback_draft(config: AppConfig, event: JobChangeEvent) -> DraftArtifact:
    subject = f"Quick congrats on your move to {event.new_company_name}"
    body = (
        f"Hi {event.person_name.split()[0]},\n\n"
        f"I saw you stepped into the {event.new_title} role at {event.new_company_name}. "
        f"Given the revops conversations we had while you were at {event.old_company_name}, "
        f"I thought it could be useful to reconnect and share a few ideas that might help as you settle in.\n\n"
        "If it would be helpful, I can send over a short point of view or we can compare notes for 15 minutes next week."
    )
    return DraftArtifact(
        subject=subject,
        body=body,
        personalization_rationale=(
            "Fallback draft references the role change and prior revops conversation context."
        ),
        confidence=0.72,
        used_facts=[
            event.person_name,
            event.new_title,
            event.new_company_name,
            event.old_company_name,
        ],
        warnings=["deterministic_fallback_used"],
        llm_provider=config.llm_provider,
        llm_model=config.llm_model,
        llm_attempt_path="deterministic_fallback",
    )
