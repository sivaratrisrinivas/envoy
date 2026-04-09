from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from app.config import AppConfig


def test_resolved_database_url_defaults_to_sqlite(tmp_path: Path) -> None:
    config = AppConfig.for_test(tmp_path, "test-secret")

    assert config.resolved_database_url == f"sqlite:///{config.db_path}"


def test_resolved_database_url_normalizes_plain_postgresql_urls(tmp_path: Path) -> None:
    config = replace(
        AppConfig.for_test(tmp_path, "test-secret"),
        database_url="postgresql://postgres:secret@postgres.railway.internal:5432/railway",
    )

    assert config.resolved_database_url == "postgresql+psycopg://postgres:secret@postgres.railway.internal:5432/railway"


def test_resolved_database_url_preserves_explicit_sqlalchemy_driver(tmp_path: Path) -> None:
    config = replace(
        AppConfig.for_test(tmp_path, "test-secret"),
        database_url="postgresql+psycopg://postgres:secret@postgres.railway.internal:5432/railway",
    )

    assert config.resolved_database_url == "postgresql+psycopg://postgres:secret@postgres.railway.internal:5432/railway"


def test_from_env_normalizes_case_for_live_mode_provider(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CRM_MODE", "AIRTABLE")
    monkeypatch.setenv("LLM_MODE", "LIVE")
    monkeypatch.setenv("LLM_PROVIDER", "Gemini")

    config = AppConfig.from_env(root_dir=tmp_path)

    assert config.crm_mode == "airtable"
    assert config.llm_mode == "live"
    assert config.llm_provider == "gemini"
    assert config.llm_provider_label == "Gemini"
