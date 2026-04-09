from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path
    webhook_secret: str
    admin_secret: str
    tenant_id: str
    demo_env: str
    crm_mode: str
    llm_mode: str
    llm_provider: str
    llm_model: str
    llm_fallback_model: str
    database_url: str | None
    gemini_api_key: str | None
    airtable_api_key: str | None
    airtable_base_id: str | None
    airtable_contacts_table: str
    airtable_accounts_table: str
    airtable_activity_table: str
    dispatch_inline: bool
    recovery_stale_after_seconds: int

    @property
    def local_dir(self) -> Path:
        return self.root_dir / ".local"

    @property
    def state_dir(self) -> Path:
        return self.local_dir / "state"

    @property
    def sqlite_dir(self) -> Path:
        return self.state_dir / "sqlite"

    @property
    def fake_crm_dir(self) -> Path:
        return self.state_dir / "fake_crm"

    @property
    def db_path(self) -> Path:
        return self.sqlite_dir / f"{self.tenant_id}__{self.demo_env}.sqlite3"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"sqlite:///{self.db_path}"

    @property
    def fake_crm_path(self) -> Path:
        return self.fake_crm_dir / f"{self.tenant_id}__{self.demo_env}.json"

    @property
    def prompts_dir(self) -> Path:
        return self.root_dir / "prompts"

    @property
    def prompt_template_path(self) -> Path:
        return self.prompts_dir / "job_change_email.md"

    @property
    def fallback_template_path(self) -> Path:
        return self.prompts_dir / "job_change_email_fallback.txt"

    @property
    def policy_path(self) -> Path:
        return self.prompts_dir / "job_change_policy.yaml"

    @classmethod
    def from_env(cls, root_dir: Path | None = None) -> "AppConfig":
        resolved_root = (root_dir or Path.cwd()).resolve()
        return cls(
            root_dir=resolved_root,
            webhook_secret=os.getenv("WEBHOOK_SECRET", "dev-secret"),
            admin_secret=os.getenv("ADMIN_SECRET", "dev-admin-secret"),
            tenant_id=os.getenv("TENANT_ID", "demo_crustdata"),
            demo_env=os.getenv("DEMO_ENV", "envoy_local_v1"),
            crm_mode=os.getenv("CRM_MODE", "fake"),
            llm_mode=os.getenv("LLM_MODE", "fake"),
            llm_provider=os.getenv("LLM_PROVIDER", "gemini"),
            llm_model=os.getenv("LLM_MODEL", "gemini-3-flash-preview"),
            llm_fallback_model=os.getenv("LLM_FALLBACK_MODEL", "gemini-2.5-flash"),
            database_url=os.getenv("DATABASE_URL"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            airtable_api_key=os.getenv("AIRTABLE_API_KEY"),
            airtable_base_id=os.getenv("AIRTABLE_BASE_ID"),
            airtable_contacts_table=os.getenv("AIRTABLE_CONTACTS_TABLE", "Contacts"),
            airtable_accounts_table=os.getenv("AIRTABLE_ACCOUNTS_TABLE", "Accounts"),
            airtable_activity_table=os.getenv("AIRTABLE_ACTIVITY_TABLE", "Activity Log"),
            dispatch_inline=os.getenv("DISPATCH_INLINE", "0") == "1",
            recovery_stale_after_seconds=max(15, int(os.getenv("RECOVERY_STALE_AFTER_SECONDS", "120"))),
        )

    @classmethod
    def for_test(cls, root_dir: Path, webhook_secret: str) -> "AppConfig":
        return cls(
            root_dir=root_dir.resolve(),
            webhook_secret=webhook_secret,
            admin_secret="test-admin-secret",
            tenant_id="demo_crustdata",
            demo_env="envoy_test_v1",
            crm_mode="fake",
            llm_mode="fake",
            llm_provider="gemini",
            llm_model="gemini-3-flash-preview",
            llm_fallback_model="gemini-2.5-flash",
            database_url=None,
            gemini_api_key=None,
            airtable_api_key=None,
            airtable_base_id=None,
            airtable_contacts_table="Contacts",
            airtable_accounts_table="Accounts",
            airtable_activity_table="Activity Log",
            dispatch_inline=True,
            recovery_stale_after_seconds=120,
        )

    def ensure_directories(self) -> None:
        self.sqlite_dir.mkdir(parents=True, exist_ok=True)
        self.fake_crm_dir.mkdir(parents=True, exist_ok=True)

    def readiness_errors(self) -> list[str]:
        errors: list[str] = []
        if self.crm_mode == "airtable":
            if not self.airtable_api_key:
                errors.append("missing AIRTABLE_API_KEY")
            if not self.airtable_base_id:
                errors.append("missing AIRTABLE_BASE_ID")
        if self.llm_mode == "live":
            if self.llm_provider == "gemini" and not self.gemini_api_key:
                errors.append("missing GEMINI_API_KEY")
        return errors
