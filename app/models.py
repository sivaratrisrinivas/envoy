from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobChangeEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_id: str
    event_type: str
    occurred_at: str
    confidence: float
    confidence_reason: str
    person_name: str
    person_linkedin_url: str
    email: str | None = None
    old_company_name: str
    old_company_domain: str
    new_company_name: str
    new_company_domain: str
    new_title: str
    trigger_reason: str
    crm_lookup_keys: dict[str, Any] = Field(default_factory=dict)
    source_payload: dict[str, Any] = Field(default_factory=dict)


class DraftArtifact(BaseModel):
    subject: str
    body: str
    personalization_rationale: str
    confidence: float
    used_facts: list[str]
    warnings: list[str]
    llm_provider: str
    llm_model: str
    llm_attempt_path: str
