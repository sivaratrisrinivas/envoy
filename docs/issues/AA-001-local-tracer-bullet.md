# AA-001: Local tracer bullet from webhook to fake CRM draft

## Type

AFK

## Status

Open

## Parent PRD

[Action Agent PRD](../action-agent-prd.md)

## What to build

Create the first thin end-to-end path through the system using a synthetic hero webhook, local execution, control-plane persistence, fake CRM behavior, and a deterministic draft artifact. This slice should prove that one command can drive the full signal-to-action loop locally, even before real Airtable or Gemini are introduced.

## Acceptance criteria

- [ ] A synthetic hero event can be triggered locally with one command and is accepted through the webhook ingress path
- [ ] The event is persisted and processed end-to-end into the fake CRM surface with a visible activity summary and draft artifact
- [ ] One automated integration test proves the local signal-to-action loop and event-level idempotency

## Blocked by

None - can start immediately

## User stories addressed

- User story 9
- User story 10
- User story 17
- User story 19
- User story 29
- User story 30
- User story 31
- User story 43
- User story 45
