from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import AppConfig
from app.models import JobChangeEvent
from app.runtime import AppRuntime


def create_app(config: AppConfig | None = None) -> FastAPI:
    resolved_config = config or AppConfig.from_env()
    runtime = AppRuntime.build(resolved_config)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        runtime.start_recovery_poller()
        try:
            yield
        finally:
            runtime.shutdown()

    app = FastAPI(docs_url=None if not resolved_config.dispatch_inline else "/docs", lifespan=lifespan)
    app.state.runtime = runtime

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz():
        errors = runtime.config.readiness_errors()
        if errors:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not_ready", "errors": errors},
            )
        return {"status": "ready"}

    @app.post("/webhook/crustdata", status_code=status.HTTP_202_ACCEPTED)
    async def ingest_crustdata_webhook(
        payload: JobChangeEvent,
        x_webhook_secret: str = Header(default=""),
    ) -> dict[str, str]:
        if x_webhook_secret != runtime.config.webhook_secret:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid webhook secret")
        runtime.handle_event(payload, raw_payload=payload.model_dump())
        return {"status": "accepted", "event_id": payload.event_id}

    return app


app = create_app()
