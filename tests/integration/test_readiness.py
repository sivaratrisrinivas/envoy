from __future__ import annotations

import asyncio
from dataclasses import replace
from pathlib import Path

import httpx

from app.config import AppConfig
from app.main import create_app


def _get_readyz(config: AppConfig) -> httpx.Response:
    async def run() -> httpx.Response:
        app = create_app(config)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/readyz")

    return asyncio.run(run())


def test_readyz_is_ready_in_fake_local_mode(tmp_path: Path) -> None:
    response = _get_readyz(AppConfig.for_test(tmp_path, "test-secret"))
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_readyz_fails_when_live_modes_are_missing_required_credentials(tmp_path: Path) -> None:
    config = replace(
        AppConfig.for_test(tmp_path, "test-secret"),
        crm_mode="airtable",
        llm_mode="live",
    )

    response = _get_readyz(config)

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
