from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Event, RLock, Thread
import time

from app.config import AppConfig
from app.crm.airtable import AirtableCRMClient
from app.crm.fake import FakeCRMClient
from app.llm.service import DraftService
from app.models import JobChangeEvent
from app.storage import ControlPlaneStore


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AppRuntime:
    config: AppConfig
    store: ControlPlaneStore
    fake_crm: FakeCRMClient
    draft_service: DraftService
    lock: RLock
    stop_event: Event
    poller_thread: Thread | None = None

    @classmethod
    def build(cls, config: AppConfig) -> "AppRuntime":
        config.ensure_directories()
        return cls(
            config=config,
            store=ControlPlaneStore(config),
            fake_crm=FakeCRMClient(config),
            draft_service=DraftService(config),
            lock=RLock(),
            stop_event=Event(),
        )

    def handle_event(self, event: JobChangeEvent, raw_payload: dict) -> str:
        with self.lock:
            inserted = self.store.record_event(event, raw_payload=raw_payload, received_at=utcnow())
            if not inserted:
                return self.store.get_event_status(event.event_id)
            if self.config.dispatch_inline:
                return self.process_event(event)
            Thread(target=self.process_event, args=(event,), daemon=True).start()
            return "accepted"

    def ingest_only(self, raw_payload: dict) -> str:
        event = JobChangeEvent.model_validate(raw_payload)
        inserted = self.store.record_event(event, raw_payload=raw_payload, received_at=utcnow())
        return "recorded" if inserted else "duplicate"

    def process_event(self, event: JobChangeEvent) -> str:
        with self.lock:

            if event.event_type != "job_change":
                self.store.update_event_status(event.event_id, status="unsupported_event_type")
                self.store.update_run(
                    event.event_id,
                    status="completed",
                    current_step="unsupported_event_type",
                    completed_steps=["record_event"],
                    heartbeat_at=utcnow(),
                )
                return "unsupported_event_type"

            if event.confidence < 0.8:
                self.store.update_event_status(event.event_id, status="non_actionable_low_confidence")
                self.store.update_run(
                    event.event_id,
                    status="completed",
                    current_step="non_actionable_low_confidence",
                    completed_steps=["record_event"],
                    heartbeat_at=utcnow(),
                )
                return "non_actionable_low_confidence"

            self.store.update_event_status(event.event_id, status="processing")
            self.store.update_run(
                event.event_id,
                status="processing",
                current_step="generate_draft",
                completed_steps=["record_event"],
                heartbeat_at=utcnow(),
            )
            crm_client = self.fake_crm if self.config.crm_mode == "fake" else AirtableCRMClient(self.config)
            draft = self.draft_service.generate(
                event,
                {
                    "ae_owner": crm_client.load_contact_context(event.person_linkedin_url).get("ae_owner", "Jordan Lee")
                },
            )
            self.store.save_artifact(event.event_id, "draft", draft, created_at=utcnow())

            self.store.update_run(
                event.event_id,
                status="processing",
                current_step="apply_crm_state",
                completed_steps=["record_event", "generate_draft"],
                heartbeat_at=utcnow(),
            )
            crm_client.apply_job_change(event, draft)

            self.store.update_event_status(event.event_id, status="completed")
            self.store.update_run(
                event.event_id,
                status="completed",
                current_step="done",
                completed_steps=["record_event", "generate_draft", "apply_crm_state"],
                heartbeat_at=utcnow(),
            )
            return "completed"

    def recover_stale_runs(self, *, stale_before: str) -> list[str]:
        recovered: list[str] = []
        for event_id in self.store.list_stale_processing_events(stale_before=stale_before):
            event = self.store.get_event(event_id)
            self.process_event(event)
            recovered.append(event_id)
        return recovered

    def replay_event(self, event_id: str) -> str:
        self.store.reset_run_for_replay(event_id, reset_at=utcnow())
        event = self.store.get_event(event_id)
        return self.process_event(event)

    def start_recovery_poller(self, interval_seconds: float = 15.0) -> None:
        if self.poller_thread is not None or self.config.dispatch_inline:
            return

        def loop() -> None:
            while not self.stop_event.is_set():
                stale_before = (
                    datetime.now(timezone.utc) - timedelta(seconds=self.config.recovery_stale_after_seconds)
                ).isoformat()
                self.recover_stale_runs(stale_before=stale_before)
                time.sleep(interval_seconds)

        self.poller_thread = Thread(target=loop, daemon=True)
        self.poller_thread.start()

    def shutdown(self) -> None:
        self.stop_event.set()
