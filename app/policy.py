from __future__ import annotations

from dataclasses import dataclass
import yaml

from app.models import DraftArtifact, JobChangeEvent


@dataclass(frozen=True)
class PolicyResult:
    valid: bool
    reasons: list[str]


class MessagePolicy:
    def __init__(self, policy_path=None) -> None:
        default_phrases = [
            "we noticed",
            "we tracked",
            "our signal",
            "watcher",
            "crustdata",
        ]
        if policy_path and getattr(policy_path, "exists", lambda: False)():
            data = yaml.safe_load(policy_path.read_text()) or {}
            self._banned_phrases = data.get("banned_phrases", default_phrases)
        else:
            self._banned_phrases = default_phrases

    def validate(self, event: JobChangeEvent, draft: DraftArtifact) -> PolicyResult:
        reasons: list[str] = []
        lowered_body = draft.body.lower()
        lowered_subject = draft.subject.lower()
        for phrase in self._banned_phrases:
            if phrase in lowered_body or phrase in lowered_subject:
                reasons.append(f"banned_phrase:{phrase}")
        if event.new_company_name.lower() not in lowered_body:
            reasons.append("missing_new_company_reference")
        if event.new_title.lower() not in lowered_body:
            reasons.append("missing_new_title_reference")
        return PolicyResult(valid=not reasons, reasons=reasons)
