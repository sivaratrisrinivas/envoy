from __future__ import annotations

from pathlib import Path

from app.config import AppConfig
from app.runtime import AppRuntime
from app.storage import ControlPlaneStore


def _hero_event() -> dict:
    return {
        "event_id": "evt_recovery_001",
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


def test_recover_stale_run_completes_pending_work(tmp_path: Path) -> None:
    config = AppConfig.for_test(tmp_path, "test-secret")
    runtime = AppRuntime.build(config)
    store = ControlPlaneStore(config)

    runtime.ingest_only(_hero_event())
    store.update_event_status("evt_recovery_001", status="processing")
    store.update_run(
        "evt_recovery_001",
        status="processing",
        current_step="generate_draft",
        completed_steps=["record_event"],
        heartbeat_at="2000-01-01T00:00:00+00:00",
    )

    recovered = runtime.recover_stale_runs(stale_before="2001-01-01T00:00:00+00:00")

    assert recovered == ["evt_recovery_001"]
    assert store.get_event_status("evt_recovery_001") == "completed"
    assert runtime.fake_crm.load_state()["activity_log"]["evt_recovery_001"]["status"] == "draft_ready"


def test_replay_event_reprocesses_failed_run(tmp_path: Path) -> None:
    config = AppConfig.for_test(tmp_path, "test-secret")
    runtime = AppRuntime.build(config)
    store = ControlPlaneStore(config)

    runtime.ingest_only(_hero_event())
    store.update_event_status("evt_recovery_001", status="failed", error="forced failure")
    store.update_run(
        "evt_recovery_001",
        status="failed",
        current_step="generate_draft",
        completed_steps=["record_event"],
        heartbeat_at="2000-01-01T00:00:00+00:00",
        error="forced failure",
    )

    runtime.replay_event("evt_recovery_001")

    assert store.get_event_status("evt_recovery_001") == "completed"
