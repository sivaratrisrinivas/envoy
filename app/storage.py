from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from sqlalchemy import create_engine, text

from app.config import AppConfig
from app.models import DraftArtifact, JobChangeEvent


SQLITE_CREATE_EVENTS = """
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  demo_env TEXT NOT NULL,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,
  confidence REAL NOT NULL,
  occurred_at TEXT NOT NULL,
  received_at TEXT NOT NULL,
  raw_payload_json TEXT NOT NULL,
  normalized_payload_json TEXT NOT NULL,
  last_error TEXT
)
"""

SQLITE_CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS workflow_runs (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  current_step TEXT,
  completed_steps_json TEXT NOT NULL,
  heartbeat_at TEXT,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""

SQLITE_CREATE_ARTIFACTS = """
CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  content_json TEXT NOT NULL,
  created_at TEXT NOT NULL
)
"""

POSTGRES_CREATE_EVENTS = """
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  demo_env TEXT NOT NULL,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,
  confidence DOUBLE PRECISION NOT NULL,
  occurred_at TEXT NOT NULL,
  received_at TEXT NOT NULL,
  raw_payload_json TEXT NOT NULL,
  normalized_payload_json TEXT NOT NULL,
  last_error TEXT
)
"""

POSTGRES_CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS workflow_runs (
  run_id BIGSERIAL PRIMARY KEY,
  event_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  current_step TEXT,
  completed_steps_json TEXT NOT NULL,
  heartbeat_at TEXT,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""

POSTGRES_CREATE_ARTIFACTS = """
CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id BIGSERIAL PRIMARY KEY,
  event_id TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  content_json TEXT NOT NULL,
  created_at TEXT NOT NULL
)
"""


@dataclass
class ControlPlaneStore:
    config: AppConfig

    def __post_init__(self) -> None:
        self.config.ensure_directories()
        self.engine = create_engine(self.config.resolved_database_url, future=True)
        self._initialize()

    def _initialize(self) -> None:
        if self.config.resolved_database_url.startswith("postgres"):
            events_sql = POSTGRES_CREATE_EVENTS
            runs_sql = POSTGRES_CREATE_RUNS
            artifacts_sql = POSTGRES_CREATE_ARTIFACTS
        else:
            events_sql = SQLITE_CREATE_EVENTS
            runs_sql = SQLITE_CREATE_RUNS
            artifacts_sql = SQLITE_CREATE_ARTIFACTS

        with self.engine.begin() as connection:
            connection.execute(text(events_sql))
            connection.execute(text(runs_sql))
            connection.execute(text(artifacts_sql))

    def record_event(self, event: JobChangeEvent, raw_payload: dict[str, Any], received_at: str) -> bool:
        with self.engine.begin() as connection:
            existing = connection.execute(
                text("SELECT event_id FROM events WHERE event_id = :event_id"),
                {"event_id": event.event_id},
            ).mappings().first()
            if existing:
                return False

            connection.execute(
                text(
                    """
                    INSERT INTO events (
                      event_id, tenant_id, demo_env, event_type, status, confidence,
                      occurred_at, received_at, raw_payload_json, normalized_payload_json, last_error
                    ) VALUES (
                      :event_id, :tenant_id, :demo_env, :event_type, :status, :confidence,
                      :occurred_at, :received_at, :raw_payload_json, :normalized_payload_json, :last_error
                    )
                    """
                ),
                {
                    "event_id": event.event_id,
                    "tenant_id": self.config.tenant_id,
                    "demo_env": self.config.demo_env,
                    "event_type": event.event_type,
                    "status": "received",
                    "confidence": event.confidence,
                    "occurred_at": event.occurred_at,
                    "received_at": received_at,
                    "raw_payload_json": json.dumps(raw_payload),
                    "normalized_payload_json": event.model_dump_json(),
                    "last_error": None,
                },
            )

            connection.execute(
                text(
                    """
                    INSERT INTO workflow_runs (
                      event_id, status, current_step, completed_steps_json, heartbeat_at, error, created_at, updated_at
                    ) VALUES (
                      :event_id, :status, :current_step, :completed_steps_json, :heartbeat_at, :error, :created_at, :updated_at
                    )
                    """
                ),
                {
                    "event_id": event.event_id,
                    "status": "pending",
                    "current_step": None,
                    "completed_steps_json": json.dumps([]),
                    "heartbeat_at": received_at,
                    "error": None,
                    "created_at": received_at,
                    "updated_at": received_at,
                },
            )
        return True

    def update_run(
        self,
        event_id: str,
        *,
        status: str,
        current_step: str | None,
        completed_steps: list[str] | None = None,
        heartbeat_at: str,
        error: str | None = None,
    ) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE workflow_runs
                    SET status = :status,
                        current_step = :current_step,
                        completed_steps_json = :completed_steps_json,
                        heartbeat_at = :heartbeat_at,
                        error = :error,
                        updated_at = :updated_at
                    WHERE event_id = :event_id
                    """
                ),
                {
                    "status": status,
                    "current_step": current_step,
                    "completed_steps_json": json.dumps(completed_steps or []),
                    "heartbeat_at": heartbeat_at,
                    "error": error,
                    "updated_at": heartbeat_at,
                    "event_id": event_id,
                },
            )

    def update_event_status(self, event_id: str, *, status: str, error: str | None = None) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text("UPDATE events SET status = :status, last_error = :error WHERE event_id = :event_id"),
                {"status": status, "error": error, "event_id": event_id},
            )

    def save_artifact(self, event_id: str, artifact_type: str, artifact: DraftArtifact, created_at: str) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO artifacts (event_id, artifact_type, content_json, created_at)
                    VALUES (:event_id, :artifact_type, :content_json, :created_at)
                    """
                ),
                {
                    "event_id": event_id,
                    "artifact_type": artifact_type,
                    "content_json": artifact.model_dump_json(),
                    "created_at": created_at,
                },
            )

    def get_event(self, event_id: str) -> JobChangeEvent:
        with self.engine.begin() as connection:
            row = connection.execute(
                text("SELECT normalized_payload_json FROM events WHERE event_id = :event_id"),
                {"event_id": event_id},
            ).mappings().first()
            if row is None:
                raise KeyError(event_id)
        return JobChangeEvent.model_validate(json.loads(row["normalized_payload_json"]))

    def get_event_status(self, event_id: str) -> str:
        with self.engine.begin() as connection:
            row = connection.execute(
                text("SELECT status FROM events WHERE event_id = :event_id"),
                {"event_id": event_id},
            ).mappings().first()
            if row is None:
                raise KeyError(event_id)
        return str(row["status"])

    def get_run(self, event_id: str) -> dict[str, Any]:
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT status, current_step, completed_steps_json, heartbeat_at, error
                    FROM workflow_runs
                    WHERE event_id = :event_id
                    """
                ),
                {"event_id": event_id},
            ).mappings().first()
            if row is None:
                raise KeyError(event_id)
        return {
            "status": row["status"],
            "current_step": row["current_step"],
            "completed_steps": json.loads(row["completed_steps_json"]),
            "heartbeat_at": row["heartbeat_at"],
            "error": row["error"],
        }

    def list_stale_processing_events(self, *, stale_before: str) -> list[str]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT event_id
                    FROM workflow_runs
                    WHERE status = 'processing' AND heartbeat_at < :stale_before
                    ORDER BY run_id ASC
                    """
                ),
                {"stale_before": stale_before},
            ).mappings().all()
        return [str(row["event_id"]) for row in rows]

    def reset_run_for_replay(self, event_id: str, *, reset_at: str) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE workflow_runs
                    SET status = 'pending',
                        current_step = NULL,
                        completed_steps_json = :completed_steps_json,
                        heartbeat_at = :heartbeat_at,
                        error = NULL,
                        updated_at = :updated_at
                    WHERE event_id = :event_id
                    """
                ),
                {
                    "completed_steps_json": json.dumps([]),
                    "heartbeat_at": reset_at,
                    "updated_at": reset_at,
                    "event_id": event_id,
                },
            )
            connection.execute(
                text("UPDATE events SET status = 'received', last_error = NULL WHERE event_id = :event_id"),
                {"event_id": event_id},
            )

    def get_artifacts(self, event_id: str) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT artifact_type, content_json
                    FROM artifacts
                    WHERE event_id = :event_id
                    ORDER BY artifact_id ASC
                    """
                ),
                {"event_id": event_id},
            ).mappings().all()
        return [
            {"artifact_type": row["artifact_type"], "content": json.loads(row["content_json"])}
            for row in rows
        ]

    def reset_namespace(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text("DELETE FROM artifacts WHERE event_id IN (SELECT event_id FROM events WHERE tenant_id = :tenant_id AND demo_env = :demo_env)"),
                {"tenant_id": self.config.tenant_id, "demo_env": self.config.demo_env},
            )
            connection.execute(
                text("DELETE FROM workflow_runs WHERE event_id IN (SELECT event_id FROM events WHERE tenant_id = :tenant_id AND demo_env = :demo_env)"),
                {"tenant_id": self.config.tenant_id, "demo_env": self.config.demo_env},
            )
            connection.execute(
                text("DELETE FROM events WHERE tenant_id = :tenant_id AND demo_env = :demo_env"),
                {"tenant_id": self.config.tenant_id, "demo_env": self.config.demo_env},
            )
