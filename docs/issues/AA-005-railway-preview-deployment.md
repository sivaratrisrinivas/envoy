# AA-005: Preview deployment on Railway with live model and hosted control plane

## Type

HITL

## Status

Open

## Parent PRD

[Action Agent PRD](../action-agent-prd.md)

## What to build

Deploy the approved hero flow to a public Railway preview using hosted persistence, real Airtable, real Gemini credentials, and a narrow public ingress surface. This slice should make the prototype externally demoable while preserving the preview safety rules defined in the PRD.

## Acceptance criteria

- [ ] The preview runs as a single-service FastAPI deployment with hosted control-plane persistence and the approved public endpoint surface
- [ ] The preview can process the hero event against the preview namespace using live Airtable and Gemini credentials
- [ ] Preview deploys remain manual and operator-controlled, with no public admin, seed, or replay surface exposed

## Blocked by

- [AA-003](./AA-003-gemini-draft-generation.md)
- [AA-004](./AA-004-real-airtable-local-demo.md)

## User stories addressed

- User story 18
- User story 27
- User story 28
- User story 32
- User story 33
- User story 47
- User story 48
- User story 50
