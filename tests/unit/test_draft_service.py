from __future__ import annotations

from dataclasses import replace

from app.config import AppConfig
from app.policy import PolicyResult
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


class ValidProvider(LLMProvider):
    def generate_structured_draft(self, event: JobChangeEvent, context: dict) -> DraftArtifact:
        return DraftArtifact(
            subject=f"Congrats on the move to {event.new_company_name}",
            body=(
                f"Hi {event.person_name.split()[0]}, congrats on your new role as {event.new_title} "
                f"at {event.new_company_name} after your time at {event.old_company_name}."
            ),
            personalization_rationale="valid draft",
            confidence=0.95,
            used_facts=[event.person_name, event.new_company_name, event.new_title, event.old_company_name],
            warnings=[],
            llm_provider="Anthropic",
            llm_model="claude-3-opus-20240229",
            llm_attempt_path="primary_model_success",
        )


class PermissivePolicy:
    def validate(self, event: JobChangeEvent, draft: DraftArtifact) -> PolicyResult:
        return PolicyResult(valid=True, reasons=[])


def _hero_event() -> JobChangeEvent:
    return JobChangeEvent.model_validate(
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


def test_policy_failure_falls_back_to_deterministic_draft(tmp_path) -> None:
    config = AppConfig.for_test(tmp_path, "test-secret")
    service = DraftService(config, provider=InvalidProvider(), repair_provider=InvalidProvider())
    event = _hero_event()

    draft = service.generate(event, {"ae_owner": "Jordan Lee"})

    assert draft.llm_attempt_path == "deterministic_fallback"
    assert draft.llm_provider == "Gemini"
    assert "deterministic_fallback_used" in draft.warnings
    assert "tracked" not in draft.body.lower()


def test_live_generation_stamps_provider_and_model_metadata(tmp_path) -> None:
    config = replace(AppConfig.for_test(tmp_path, "test-secret"), llm_mode="live")
    service = DraftService(config, provider=ValidProvider(), repair_provider=ValidProvider(), policy=PermissivePolicy())

    draft = service.generate(_hero_event(), {"ae_owner": "Jordan Lee"})

    assert draft.llm_provider == "Gemini"
    assert draft.llm_model == "gemini-3-flash-preview"
    assert draft.llm_attempt_path == "primary_model_success"
