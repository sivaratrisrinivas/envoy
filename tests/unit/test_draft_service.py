from __future__ import annotations

from app.config import AppConfig
from app.llm.service import DraftService, LLMProvider
from app.models import DraftArtifact, JobChangeEvent


class InvalidProvider(LLMProvider):
    def generate_structured_draft(self, event: JobChangeEvent, context: dict) -> DraftArtifact:
        return DraftArtifact(
            subject="We noticed your move",
            body="We noticed your move and tracked the signal.",
            personalization_rationale="bad draft",
            confidence=0.99,
            used_facts=[event.person_name],
            warnings=[],
            llm_provider="test",
            llm_model="invalid",
            llm_attempt_path="primary_model_success",
        )


def test_policy_failure_falls_back_to_deterministic_draft(tmp_path) -> None:
    config = AppConfig.for_test(tmp_path, "test-secret")
    service = DraftService(config, provider=InvalidProvider(), repair_provider=InvalidProvider())
    event = JobChangeEvent.model_validate(
        {
            "event_id": "evt_policy",
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
            "crm_lookup_keys": {},
            "source_payload": {},
        }
    )

    draft = service.generate(event, {"ae_owner": "Jordan Lee"})

    assert draft.llm_attempt_path == "deterministic_fallback"
    assert "deterministic_fallback_used" in draft.warnings
    assert "tracked" not in draft.body.lower()
