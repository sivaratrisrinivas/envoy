# AA-003: Gemini-powered draft generation with guardrails

## Type

AFK

## Status

Open

## Parent PRD

[Action Agent PRD](../action-agent-prd.md)

## What to build

Replace deterministic draft generation with the real Gemini-driven draft path while preserving the same application-level draft contract. This slice should include structured output, prompt-policy enforcement, repair behavior, backup-model behavior, and deterministic fallback, all in support of one send-ready owner-voice draft.

## Acceptance criteria

- [ ] The workflow can generate one structured draft artifact through Gemini using the approved schema-constrained response path
- [ ] Policy validation catches unsafe or off-strategy output and routes through repair or deterministic fallback as needed
- [ ] Draft provenance records whether the artifact came from the primary model, backup model, or deterministic fallback path

## Blocked by

- [AA-002](./AA-002-hero-crm-resolution.md)

## User stories addressed

- User story 2
- User story 5
- User story 6
- User story 12
- User story 24
- User story 25
- User story 26
- User story 30
- User story 31
- User story 35
- User story 36
- User story 39
- User story 48
- User story 49
