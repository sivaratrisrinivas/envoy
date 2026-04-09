# AA-002: Hero CRM resolution for known contact to net-new account

## Type

AFK

## Status

Open

## Parent PRD

[Action Agent PRD](../action-agent-prd.md)

## What to build

Extend the local tracer bullet into the real hero business path: a known contact moves to a net-new company, the destination account is created, the contact state is updated with former/current company context, and the business-facing activity summary reflects the opportunity. This slice should make the fake CRM behavior match the intended sales story from the PRD.

## Acceptance criteria

- [ ] The workflow resolves a known contact deterministically and creates a net-new destination account when no exact account match exists
- [ ] The contact state reflects the move, including current account, former account, and draft-facing fields required by the demo
- [ ] The fake CRM activity summary and rep note clearly describe the business outcome of the move

## Blocked by

- [AA-001](./AA-001-local-tracer-bullet.md)

## User stories addressed

- User story 1
- User story 3
- User story 7
- User story 8
- User story 13
- User story 14
- User story 15
- User story 16
- User story 38
- User story 41
- User story 42
