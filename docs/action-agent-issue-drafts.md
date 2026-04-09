# Action Agent Issue Drafts

These drafts convert the approved PRD breakdown into issue-ready vertical slices.

Current blocker:
- The PRD is local Markdown, not a live GitHub issue
- This workspace is not a Git checkout
- Local `gh` authentication is invalid

When GitHub access is restored:
1. Create the parent PRD issue from `docs/action-agent-prd.md`
2. Replace `PRD-ISSUE-TBD` below with the real issue number
3. Create the slice issues in the order listed here
4. Replace slice references in `Blocked by` with real issue numbers as they are created

## Slice 1: Local tracer bullet from webhook to fake CRM draft

Type: AFK

```md
## Parent PRD

#PRD-ISSUE-TBD

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
```

## Slice 2: Hero CRM resolution for known contact to net-new account

Type: AFK

```md
## Parent PRD

#PRD-ISSUE-TBD

## What to build

Extend the local tracer bullet into the real hero business path: a known contact moves to a net-new company, the destination account is created, the contact state is updated with former/current company context, and the business-facing activity summary reflects the opportunity. This slice should make the fake CRM behavior match the intended sales story from the PRD.

## Acceptance criteria

- [ ] The workflow resolves a known contact deterministically and creates a net-new destination account when no exact account match exists
- [ ] The contact state reflects the move, including current account, former account, and draft-facing fields required by the demo
- [ ] The fake CRM activity summary and rep note clearly describe the business outcome of the move

## Blocked by

- Blocked by Slice 1

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
```

## Slice 3: Gemini-powered draft generation with guardrails

Type: AFK

```md
## Parent PRD

#PRD-ISSUE-TBD

## What to build

Replace deterministic draft generation with the real Gemini-driven draft path while preserving the same application-level draft contract. This slice should include structured output, prompt-policy enforcement, repair behavior, backup-model behavior, and deterministic fallback, all in support of one send-ready owner-voice draft.

## Acceptance criteria

- [ ] The workflow can generate one structured draft artifact through Gemini using the approved schema-constrained response path
- [ ] Policy validation catches unsafe or off-strategy output and routes through repair or deterministic fallback as needed
- [ ] Draft provenance records whether the artifact came from the primary model, backup model, or deterministic fallback path

## Blocked by

- Blocked by Slice 2

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
```

## Slice 4: Real Airtable local demo path

Type: HITL

```md
## Parent PRD

#PRD-ISSUE-TBD

## What to build

Connect the hero workflow to the real Airtable demo base in a local execution path so the business-facing before/after state is visible in the actual CRM-like surface. This slice should turn the already-working local fake flow into a local live-demo flow with curated demo data and clear activity visibility.

## Acceptance criteria

- [ ] The local hero path updates the real Airtable demo namespace with contact, account, and activity-log changes
- [ ] A seeded local demo baseline exists so the before/after state change is obvious and repeatable
- [ ] The local live-demo flow can be rehearsed manually from trigger to Airtable-visible result

## Blocked by

- Blocked by Slice 2

## User stories addressed

- User story 3
- User story 4
- User story 7
- User story 14
- User story 15
- User story 17
- User story 29
- User story 41
- User story 42
- User story 46
```

## Slice 5: Preview deployment on Railway with live model and hosted control plane

Type: HITL

```md
## Parent PRD

#PRD-ISSUE-TBD

## What to build

Deploy the approved hero flow to a public Railway preview using hosted persistence, real Airtable, real Gemini credentials, and a narrow public ingress surface. This slice should make the prototype externally demoable while preserving the preview safety rules defined in the PRD.

## Acceptance criteria

- [ ] The preview runs as a single-service FastAPI deployment with hosted control-plane persistence and the approved public endpoint surface
- [ ] The preview can process the hero event against the preview namespace using live Airtable and Gemini credentials
- [ ] Preview deploys remain manual and operator-controlled, with no public admin, seed, or replay surface exposed

## Blocked by

- Blocked by Slice 3
- Blocked by Slice 4

## User stories addressed

- User story 18
- User story 27
- User story 28
- User story 32
- User story 33
- User story 47
- User story 48
- User story 50
```

## Slice 6: Resilience and operator safety flows

Type: AFK

```md
## Parent PRD

#PRD-ISSUE-TBD

## What to build

Add the control-plane resilience behaviors that make the prototype safe to replay, recover, and operate repeatedly. This slice should cover event idempotency, bounded retries, stale-run recovery, resume behavior, and local operator workflows for replay and reset.

## Acceptance criteria

- [ ] Duplicate delivery of the same event does not create duplicate business-facing results
- [ ] Stale or interrupted runs can be resumed or replayed safely according to the approved recovery policy
- [ ] Local operator workflows exist to inspect, replay, and reset the demo state without exposing those controls publicly

## Blocked by

- Blocked by Slice 1

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
```

## Slice 7: Demo choreography and preview reset workflow

Type: HITL

```md
## Parent PRD

#PRD-ISSUE-TBD

## What to build

Finalize the operator-facing demo experience: the primary Railway preview path, the fallback local path, the preview reset workflow, and the written runbook that makes the prototype reproducible under demo conditions. This slice should turn the working system into a rehearsable presentation asset.

## Acceptance criteria

- [ ] A written demo runbook exists for the primary preview path and the fallback local path
- [ ] A privileged preview reset workflow can restore the preview namespace and supporting state before a demo
- [ ] The demo can be rehearsed end-to-end with a clear before/after presentation flow

## Blocked by

- Blocked by Slice 4
- Blocked by Slice 5
- Blocked by Slice 6

## User stories addressed

- User story 4
- User story 17
- User story 18
- User story 34
- User story 46
- User story 50
```
