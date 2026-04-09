# AA-007: Demo choreography and preview reset workflow

## Type

HITL

## Status

Open

## Parent PRD

[Action Agent PRD](../action-agent-prd.md)

## What to build

Finalize the operator-facing demo experience: the primary Railway preview path, the fallback local path, the preview reset workflow, and the written runbook that makes the prototype reproducible under demo conditions. This slice should turn the working system into a rehearsable presentation asset.

## Acceptance criteria

- [ ] A written demo runbook exists for the primary preview path and the fallback local path
- [ ] A privileged preview reset workflow can restore the preview namespace and supporting state before a demo
- [ ] The demo can be rehearsed end-to-end with a clear before/after presentation flow

## Blocked by

- [AA-004](./AA-004-real-airtable-local-demo.md)
- [AA-005](./AA-005-railway-preview-deployment.md)
- [AA-006](./AA-006-resilience-operator-safety.md)

## User stories addressed

- User story 4
- User story 17
- User story 18
- User story 34
- User story 46
- User story 50
