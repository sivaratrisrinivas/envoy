from __future__ import annotations

from typing import Protocol

from app.config import AppConfig
from app.llm.fallback import generate_fallback_draft
from app.llm.gemini import GeminiProvider
from app.models import DraftArtifact, JobChangeEvent
from app.policy import MessagePolicy


class LLMProvider(Protocol):
    def generate_structured_draft(self, event: JobChangeEvent, context: dict) -> DraftArtifact:
        ...


class DraftService:
    def __init__(
        self,
        config: AppConfig,
        *,
        provider: LLMProvider | None = None,
        repair_provider: LLMProvider | None = None,
        policy: MessagePolicy | None = None,
    ) -> None:
        self.config = config
        self.provider = provider if provider is not None else self._provider_from_config(config, config.llm_model)
        self.repair_provider = repair_provider or provider
        if self.repair_provider is None and self.provider is not None:
            self.repair_provider = self._provider_from_config(config, config.llm_fallback_model)
        self.policy = policy or MessagePolicy(config.policy_path)

    @staticmethod
    def _provider_from_config(config: AppConfig, model_name: str) -> LLMProvider | None:
        if config.llm_mode != "live":
            return None
        if config.llm_provider == "gemini" and config.gemini_api_key:
            return GeminiProvider(config, model_name=model_name)
        return None

    def generate(self, event: JobChangeEvent, context: dict) -> DraftArtifact:
        if self.provider is None or self.config.llm_mode == "fake":
            return generate_fallback_draft(self.config, event)

        primary = self.provider.generate_structured_draft(event, context)
        if self.policy.validate(event, primary).valid:
            return primary

        if self.repair_provider is not None:
            repaired = self.repair_provider.generate_structured_draft(event, context)
            if self.policy.validate(event, repaired).valid:
                return repaired

        return generate_fallback_draft(self.config, event)
