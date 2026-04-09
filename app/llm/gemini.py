from __future__ import annotations

from google import genai
from google.genai import types

from app.config import AppConfig
from app.models import DraftArtifact, JobChangeEvent


class GeminiProvider:
    def __init__(self, config: AppConfig, *, model_name: str) -> None:
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiProvider")
        self.client = genai.Client(api_key=config.gemini_api_key)
        self.model_name = model_name

    def generate_structured_draft(self, event: JobChangeEvent, context: dict) -> DraftArtifact:
        prompt = (
            "Draft a concise outbound email for a sales rep.\n"
            f"Contact: {event.person_name}\n"
            f"New title: {event.new_title}\n"
            f"New company: {event.new_company_name}\n"
            f"Former company: {event.old_company_name}\n"
            f"Trigger reason: {event.trigger_reason}\n"
            f"Owner: {context.get('ae_owner', 'Jordan Lee')}\n"
            "Constraints: owner voice, mention the move naturally, avoid surveillance language, no fabricated history."
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                responseMimeType="application/json",
                responseSchema=DraftArtifact,
            ),
        )
        parsed = response.parsed
        if isinstance(parsed, DraftArtifact):
            return parsed
        return DraftArtifact.model_validate(parsed)
