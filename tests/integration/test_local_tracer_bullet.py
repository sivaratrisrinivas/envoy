from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from app.config import AppConfig
from app.crm.fake import FakeCRMClient
from app.main import create_app


def _hero_event() -> dict:
    return {
        "event_id": "evt_hero_001",
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
        "crm_lookup_keys": {
            "linkedin_url": "https://linkedin.com/in/priyanair",
            "old_company_domain": "northstar.example",
            "new_company_domain": "acmefrontier.example",
        },
        "source_payload": {
            "provider": "crustdata-like",
            "event": "job_change",
        },
    }


def test_local_webhook_updates_fake_crm_and_creates_draft(tmp_path: Path) -> None:
    async def run_test() -> None:
        config = AppConfig.for_test(
            root_dir=tmp_path,
            webhook_secret="test-secret",
        )
        app = create_app(config)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/webhook/crustdata",
                json=_hero_event(),
                headers={"X-Webhook-Secret": "test-secret"},
            )

        assert response.status_code == 202
        fake_crm = FakeCRMClient(config)
        state = fake_crm.load_state()

        assert state["contacts"]["https://linkedin.com/in/priyanair"]["current_account"] == "Acme Frontier"
        assert state["contacts"]["https://linkedin.com/in/priyanair"]["draft_subject"]
        assert state["accounts"]["acmefrontier.example"]["account_name"] == "Acme Frontier"
        assert state["activity_log"]["evt_hero_001"]["status"] == "draft_ready"

    asyncio.run(run_test())
