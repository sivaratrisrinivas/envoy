# AA-006: Resilience and operator safety flows

## Type

AFK

## Status

Open

## Parent PRD

[Action Agent PRD](../action-agent-prd.md)

## What to build

Add the control-plane resilience behaviors that make the prototype safe to replay, recover, and operate repeatedly. This slice should cover event idempotency, bounded retries, stale-run recovery, resume behavior, and local operator workflows for replay and reset.

## Acceptance criteria

- [ ] Duplicate delivery of the same event does not create duplicate business-facing results
- [ ] Stale or interrupted runs can be resumed or replayed safely according to the approved recovery policy
- [ ] Local operator workflows exist to inspect, replay, and reset the demo state without exposing those controls publicly

## Blocked by

- [AA-001](./AA-001-local-tracer-bullet.md)

## User stories addressed

- User story 9
- User story 20
- User story 21
- User story 22
- User story 23
- User story 27
- User story 28
- User story 34
- User story 37
- User story 43
