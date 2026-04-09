from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from app.config import AppConfig
from app.crm.fake import FakeCRMClient
from app.main import create_app
from app.storage import ControlPlaneStore


def _base_event(**overrides: object) -> dict:
    payload = {
        "event_id": "evt_case_001",
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
    payload.update(overrides)
    return payload


def _post_event(config: AppConfig, payload: dict) -> httpx.Response:
    async def run() -> httpx.Response:
        app = create_app(config)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                "/webhook/crustdata",
                json=payload,
                headers={"X-Webhook-Secret": config.webhook_secret},
            )

    return asyncio.run(run())


def test_known_contact_move_preserves_owner_and_relationship_memory(tmp_path: Path) -> None:
    config = AppConfig.for_test(tmp_path, "test-secret")
    fake_crm = FakeCRMClient(config)
    fake_crm.save_state(
        {
            "contacts": {
                "https://linkedin.com/in/priyanair": {
                    "full_name": "Priya Nair",
                    "linkedin_url": "https://linkedin.com/in/priyanair",
                    "current_account": "Northstar Cloud",
                    "former_account": "Southwind Analytics",
                    "ae_owner": "Jordan Lee",
                    "relationship_memory": "Priya previously evaluated pipeline tooling with Jordan while at Northstar Cloud.",
                }
            },
            "accounts": {
                "northstar.example": {
                    "account_name": "Northstar Cloud",
                    "domain": "northstar.example",
                    "status": "active",
                }
            },
            "activity_log": {},
        }
    )

    response = _post_event(config, _base_event())

    assert response.status_code == 202
    state = fake_crm.load_state()
    contact = state["contacts"]["https://linkedin.com/in/priyanair"]
    assert contact["ae_owner"] == "Jordan Lee"
    assert contact["former_account"] == "Northstar Cloud"
    assert contact["current_account"] == "Acme Frontier"
    assert contact["relationship_memory"].startswith("Priya previously evaluated")
    assert state["accounts"]["acmefrontier.example"]["status"] == "watchlist_generated"


def test_low_confidence_event_is_persisted_but_not_actioned(tmp_path: Path) -> None:
    config = AppConfig.for_test(tmp_path, "test-secret")

    response = _post_event(
        config,
        _base_event(
            event_id="evt_low_conf",
            confidence=0.4,
            confidence_reason="uncertain_signal",
        ),
    )

    assert response.status_code == 202
    fake_crm = FakeCRMClient(config)
    state = fake_crm.load_state()
    store = ControlPlaneStore(config)
    assert state["contacts"] == {}
    assert store.get_event_status("evt_low_conf") == "non_actionable_low_confidence"


def test_duplicate_event_does_not_duplicate_activity_rows(tmp_path: Path) -> None:
    config = AppConfig.for_test(tmp_path, "test-secret")

    first = _post_event(config, _base_event(event_id="evt_dupe"))
    second = _post_event(config, _base_event(event_id="evt_dupe"))

    assert first.status_code == 202
    assert second.status_code == 202
    state = FakeCRMClient(config).load_state()
    assert list(state["activity_log"]) == ["evt_dupe"]
