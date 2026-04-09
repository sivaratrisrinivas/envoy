# Envoy Action Agent

Envoy is a small FastAPI app that turns a watcher-style `job_change` event into a GTM action.

It does four main things:
- accepts a webhook at `POST /webhook/crustdata`
- stores the event in a local control plane
- generates one outreach draft
- updates either a fake CRM or Airtable

## What It Is

This repo is a prototype for a very specific demo story:
- a known champion changes jobs
- the new company is a net-new target account
- Envoy notices the move
- Envoy creates the account context
- Envoy drafts a follow-up email for the owning rep

The app supports:
- local fake CRM mode for fast offline testing
- live Airtable mode for a visible demo
- fake draft mode
- live Gemini draft mode
- local SQLite by default
- Railway preview deployment via `scripts/deploy_preview.py`

## Why It Exists

The goal is to show one clear business moment, not a huge platform:
- one trigger
- one visible CRM change
- one usable draft
- one clean before-and-after demo

That keeps the product story easy to understand and easy to show live.

## How It Works

High-level flow:
1. a `job_change` payload hits `/webhook/crustdata`
2. the app validates the secret and the payload shape
3. the event is stored in SQLite or Postgres
4. the draft service creates a `DraftArtifact`
5. the CRM layer writes the contact, account, and activity summary

Main pieces:
- `app/main.py`: FastAPI app and routes
- `app/runtime.py`: event handling, processing, and recovery loop
- `app/storage.py`: control-plane persistence
- `app/crm/fake.py`: local fake CRM
- `app/crm/airtable.py`: Airtable integration
- `app/llm/service.py`: draft generation orchestration
- `app/llm/gemini.py`: Gemini client
- `scripts/`: setup, seeding, replay, reset, send-event, and deploy helpers

## Requirements

- Python `3.10+`
- a virtualenv at `./.venv`
- for live Airtable mode:
  - Airtable PAT
  - Airtable base ID
- for live Gemini mode:
  - `GEMINI_API_KEY`
- optional for preview deploys:
  - Railway CLI

## Config

Start from the example file:

```bash
cp .env.example .env.local
```

This app reads environment variables from the shell, so load them before running commands:

```bash
set -a
source .env.local
set +a
```

Important variables:
- `WEBHOOK_SECRET`: shared secret for the webhook
- `ADMIN_SECRET`: local admin secret used by operator scripts
- `TENANT_ID`: tenant namespace
- `DEMO_ENV`: demo namespace such as `envoy_local_v1`
- `CRM_MODE`: `fake` or `airtable`
- `LLM_MODE`: `fake` or `live`
- `LLM_PROVIDER`: `gemini`
- `LLM_MODEL`: default is `gemini-3-flash-preview`
- `LLM_FALLBACK_MODEL`: default is `gemini-2.5-flash`
- `GEMINI_API_KEY`: required in live LLM mode
- `AIRTABLE_API_KEY`: required in Airtable mode
- `AIRTABLE_BASE_ID`: required in Airtable mode
- `AIRTABLE_CONTACTS_TABLE`: default `Contacts`
- `AIRTABLE_ACCOUNTS_TABLE`: default `Accounts`
- `AIRTABLE_ACTIVITY_TABLE`: default `Activity Log`

Useful extra variables not shown in `.env.example`:
- `DISPATCH_INLINE=1`: runs the workflow inline so the local demo feels immediate
- `DATABASE_URL=...`: use Postgres instead of local SQLite

## Quick Start

Install and bootstrap:

```bash
./.venv/bin/python scripts/bootstrap.py
```

Seed demo data:

```bash
./.venv/bin/python scripts/seed_demo.py
```

Run the app:

```bash
./.venv/bin/python -m uvicorn app.main:app --reload
```

Send the hero event from a second shell:

```bash
set -a
source .env.local
set +a
./.venv/bin/python scripts/send_event.py --scenario hero_job_change
```

Health checks:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

## Demo Modes

### Local Fake Demo

Use this when you want the fastest no-credential path.

Recommended `.env.local` values:

```bash
WEBHOOK_SECRET=envoy-demo-secret
ADMIN_SECRET=envoy-demo-admin
TENANT_ID=demo_crustdata
DEMO_ENV=envoy_local_v1
CRM_MODE=fake
LLM_MODE=fake
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3-flash-preview
LLM_FALLBACK_MODEL=gemini-2.5-flash
DISPATCH_INLINE=1
```

Run it:

```bash
set -a
source .env.local
set +a
make bootstrap
make seed
make dev
```

In a second shell:

```bash
set -a
source .env.local
set +a
make send-hero
```

What to inspect:
- `.local/state/fake_crm/<tenant>__<demo_env>.json`
- `.local/state/sqlite/<tenant>__<demo_env>.sqlite3`

### Live Airtable + Live Gemini Demo

Use this when you want the visible CRM story.

Recommended `.env.local` values:

```bash
WEBHOOK_SECRET=envoy-demo-secret
ADMIN_SECRET=envoy-demo-admin
TENANT_ID=demo_crustdata
DEMO_ENV=envoy_local_v1
CRM_MODE=airtable
LLM_MODE=live
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3-flash-preview
LLM_FALLBACK_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your-gemini-key
AIRTABLE_API_KEY=your-airtable-pat
AIRTABLE_BASE_ID=your-base-id
AIRTABLE_CONTACTS_TABLE=Contacts
AIRTABLE_ACCOUNTS_TABLE=Accounts
AIRTABLE_ACTIVITY_TABLE=Activity Log
DISPATCH_INLINE=1
```

Run it:

```bash
set -a
source .env.local
set +a
make bootstrap
make seed
make dev
```

In a second shell:

```bash
set -a
source .env.local
set +a
make send-hero
```

Expected Airtable result:
- `Contacts`: the hero contact is updated
- `Accounts`: the destination account appears
- `Activity Log`: one event summary row appears

## Railway Demo Sequence

Use the public preview URL without a trailing dot:

```text
https://envoy-api-preview.up.railway.app
```

Run this from the repo root in WSL.

Prep:

```bash
cd /home/srinivas/workspace/github.com/sivaratrisrinivas/envoy
set -a
source .env.local
set +a
```

Health check the deployed app:

```bash
curl https://envoy-api-preview.up.railway.app/healthz
curl https://envoy-api-preview.up.railway.app/readyz
```

Trigger the hero event against Railway:

```bash
./.venv/bin/python scripts/send_event.py \
  --scenario hero_job_change \
  --server https://envoy-api-preview.up.railway.app
```

Or with `make` plus the raw script if you want the URL visible in the command:

```bash
./.venv/bin/python scripts/send_event.py \
  --scenario hero_job_change \
  --server https://envoy-api-preview.up.railway.app \
  --secret "$WEBHOOK_SECRET"
```

Then show:
- before: the contact at the old company and no destination account in Airtable
- trigger: the `send_event.py` command pointed at Railway
- after: the new account, updated contact, activity row, and draft

## Local Fallback Sequence

If Railway is unhealthy right before the demo, use the local path instead.

Shell 1:

```bash
cd /home/srinivas/workspace/github.com/sivaratrisrinivas/envoy
set -a
source .env.local
set +a
make bootstrap
make seed
make dev
```

Shell 2:

```bash
cd /home/srinivas/workspace/github.com/sivaratrisrinivas/envoy
set -a
source .env.local
set +a
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
make send-hero
```

## Make Targets

- `make bootstrap`: initialize local control-plane state
- `make dev`: start the FastAPI app with reload
- `make test`: run tests
- `make seed`: seed the fake CRM or Airtable namespace
- `make send-hero`: send the main hero event
- `make send-backup`: send the backup event
- `make replay EVENT_ID=...`: replay one stored event
- `make reset-preview CONFIRM=preview`: run the protected preview reset script
- `make deploy-preview`: run the Railway deploy helper

## Files Worth Knowing

- `docs/demo-runbook.md`: demo choreography
- `docs/action-agent-prd.md`: product spec
- `docs/issues/`: local issue tracker
- `.env.example`: config template

## Notes

- The app only supports `job_change` as the real hero flow today.
- `dispatch_inline` is helpful for demos because the result appears right after the webhook call.
- Airtable and Gemini secrets should stay in an untracked `.env.local`.
- If secrets were pasted into chat, rotate them after setup.

## Plain-English Demo Guide

Here is the short, simple version in plain language:

Load your env file, stay in this repo, and use the Railway URL, not localhost. Run `curl https://envoy-api-preview.up.railway.app/healthz` and `curl https://envoy-api-preview.up.railway.app/readyz` first. If both are good, send the hero event with `./.venv/bin/python scripts/send_event.py --scenario hero_job_change --server https://envoy-api-preview.up.railway.app`. Then refresh Airtable and show the result. You want the contact updated, the new account created, the activity row added, and the draft ready. Keep the local flow only as backup. If Railway acts weird, switch fast, stay calm, and keep the story moving. That is the whole demo flow for the room today. Open the right Airtable views before people start watching.
