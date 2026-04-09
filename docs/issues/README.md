# Action Agent Local Issues

This directory is the local issue tracker for the Action Agent prototype.

Parent PRD:
- [Action Agent PRD](../action-agent-prd.md)

Issue order:
1. [AA-001: Local tracer bullet from webhook to fake CRM draft](./AA-001-local-tracer-bullet.md)
2. [AA-002: Hero CRM resolution for known contact to net-new account](./AA-002-hero-crm-resolution.md)
3. [AA-003: Gemini-powered draft generation with guardrails](./AA-003-gemini-draft-generation.md)
4. [AA-004: Real Airtable local demo path](./AA-004-real-airtable-local-demo.md)
5. [AA-005: Preview deployment on Railway with live model and hosted control plane](./AA-005-railway-preview-deployment.md)
6. [AA-006: Resilience and operator safety flows](./AA-006-resilience-operator-safety.md)
7. [AA-007: Demo choreography and preview reset workflow](./AA-007-demo-choreography-preview-reset.md)

Quick view:

| ID | Title | Type | Blocked by |
|---|---|---|---|
| AA-001 | Local tracer bullet from webhook to fake CRM draft | AFK | None |
| AA-002 | Hero CRM resolution for known contact to net-new account | AFK | AA-001 |
| AA-003 | Gemini-powered draft generation with guardrails | AFK | AA-002 |
| AA-004 | Real Airtable local demo path | HITL | AA-002 |
| AA-005 | Preview deployment on Railway with live model and hosted control plane | HITL | AA-003, AA-004 |
| AA-006 | Resilience and operator safety flows | AFK | AA-001 |
| AA-007 | Demo choreography and preview reset workflow | HITL | AA-004, AA-005, AA-006 |

Status convention:
- `Open`
- `In Progress`
- `Blocked`
- `Done`
