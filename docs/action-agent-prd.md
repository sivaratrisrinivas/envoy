## Problem Statement

CrustData can already surface valuable commercial signals, but those signals still stop at "data delivery." In practice, sales teams do not get value merely from receiving a webhook payload about a champion changing jobs. They get value when that signal turns into immediate, relevant sales action inside the systems they already use.

From the user's perspective, the current problem is the "last-mile execution gap." A sales team can know that a high-value contact moved to a new company, but someone still has to notice the signal, look up the person, update the CRM, determine whether the destination company should become a target account, remember the history of the relationship, and write outbound messaging. That manual work is slow, inconsistent, and easy to drop on the floor. As a result, time-sensitive signals decay before they become pipeline.

The user wants a prototype that proves CrustData-like watcher events can autonomously drive real GTM execution. The prototype must visibly update a CRM-like system, preserve relationship context, and generate a personalized outbound draft fast enough to demo live. It should feel like "set it and forget it," not like a human-in-the-loop workflow disguised as automation.

## Solution

Build an Action Agent prototype that receives a synthetic CrustData-like `job_change` webhook, normalizes it into a stable internal event contract, and automatically executes a deterministic sales workflow. The system updates a CRM-like Airtable base, creates a new destination account when needed, updates the champion's contact record, logs the business event, and drafts a personalized outbound email in the account owner's voice.

The prototype prioritizes one hero scenario: a known champion leaves an existing customer or target account and joins a net-new company. The system operationalizes that signal in under 10 seconds and shows the results directly in Airtable so the demo audience can see the before/after state change clearly. The draft is generated with Gemini, constrained through structured output and policy checks, and never sent automatically.

The solution is intentionally split between deterministic workflow logic and model-generated communication. Deterministic code owns matching, CRM mutations, idempotency, retries, and auditability. The model owns the quality of the draft. This keeps the system reliable enough to trust while still delivering the "wow" moment of timely, contextual outbound generation.

## User Stories

1. As an account executive, I want a champion job-change signal to automatically update my CRM context, so that I can act on the opportunity without manual research.
2. As an SDR, I want a relevant outbound draft to appear automatically when a known contact moves companies, so that I can follow up while the signal is still fresh.
3. As a revenue operations lead, I want watcher signals to create CRM-visible state changes, so that data providers feel operational rather than informational.
4. As a demo audience member, I want to see a clear before-and-after CRM transformation, so that the value of the automation is immediately obvious.
5. As an AE, I want the draft written in my voice rather than a generic team voice, so that the output feels sendable with minimal edits.
6. As an SDR manager, I want the system to stage drafts without sending them, so that the workflow feels powerful without introducing external communication risk.
7. As a RevOps user, I want the system to create a destination account automatically when a champion lands at a net-new company, so that new pipeline surfaces are captured immediately.
8. As an AE, I want the contact record to show both the former and current company after a move, so that I can understand the relationship transition at a glance.
9. As an operator, I want the workflow to be idempotent by event ID, so that replaying or redelivering a signal does not create duplicate CRM artifacts.
10. As a developer, I want a normalized internal event schema separate from the provider payload, so that the core system stays stable even if upstream payload shapes change.
11. As an engineer, I want deterministic CRM mutation logic, so that record resolution and updates are reproducible and testable.
12. As a product lead, I want the model to be responsible only for the message draft, so that the "agentic" story does not compromise system correctness.
13. As a sales user, I want the destination company to become a visible target account when a champion arrives there, so that I can convert relationship history into new pipeline.
14. As a CRM user, I want an activity log entry summarizing what happened for each signal, so that I can understand why the system acted.
15. As an AE, I want the contact record to show the latest draft subject and body directly, so that I do not need to open a separate tool to use the output.
16. As a sales leader, I want a short internal rep note describing why the outreach matters now, so that the opportunity can be understood quickly during pipeline review.
17. As a demo operator, I want to trigger the hero event with one command, so that the live demo is reliable and repeatable.
18. As a demo operator, I want a fallback local path if the hosted preview has issues, so that the demo remains resilient under pressure.
19. As an engineer, I want the system to return `202 Accepted` quickly on webhook ingest, so that the ingress path stays reliable and decoupled from downstream latency.
20. As an operator, I want a recovery poller for stuck runs, so that transient failures do not require constant manual babysitting.
21. As an engineer, I want runs to resume from the last incomplete step when possible, so that partial progress is not lost on recovery.
22. As a product owner, I want unsupported or low-confidence events persisted but not actioned, so that the platform can distinguish ingestion from automation.
23. As a GTM systems owner, I want low-confidence signals to remain visible as non-actionable, so that the platform's trust boundary is explicit.
24. As a data-conscious user, I want the draft to avoid creepy "we tracked your move" language, so that the outreach feels human rather than surveillant.
25. As an AE, I want the message to reference a real relationship memory or prior context, so that the outreach sounds authentic rather than templated.
26. As a product stakeholder, I want optional enrichment to improve draft quality without blocking the workflow, so that the system stays fast enough for a live demo.
27. As a platform operator, I want local development to use SQLite while the hosted preview uses Postgres, so that development stays lightweight without making the preview fragile.
28. As an engineer, I want one storage abstraction across local and preview modes, so that persistence behavior can change by environment without rewriting business logic.
29. As a developer, I want a fake CRM adapter that behaves like the Airtable model, so that integration tests can prove the workflow without needing live Airtable access.
30. As a developer, I want a deterministic fallback drafting path, so that model instability does not make the whole system fail.
31. As a product manager, I want the draft artifact to have one stable schema regardless of source, so that downstream UI and persistence stay simple.
32. As a security-conscious operator, I want the preview ingress protected by a shared secret and light request guards, so that a public preview does not become an open abuse surface.
33. As a preview operator, I want admin endpoints disabled publicly, so that the hosted demo exposes only the product path and not the maintenance toolbox.
34. As a maintainer, I want preview resets to be explicit, privileged operator actions, so that demo state is not accidentally destroyed.
35. As an engineer, I want prompt versions and model paths recorded per draft, so that output provenance is inspectable.
36. As a product owner, I want messaging policy rules versioned separately from prompt content, so that tone and safety constraints can evolve without entangling workflow logic.
37. As an engineer, I want a small, deep workflow runner module, so that retries, heartbeats, recovery, and serialization are encapsulated behind one stable interface.
38. As a developer, I want CRM resolution logic in one deep module, so that matching, creation, ambiguity handling, and adapter behavior can be tested independently.
39. As a developer, I want draft generation hidden behind one LLM interface, so that provider-specific SDK details do not leak through the codebase.
40. As a PM, I want the first prototype to optimize for one compelling hero path rather than a broad event matrix, so that the system tells a sharp story.
41. As a RevOps stakeholder, I want the hero path to use a known contact moving to a net-new company, so that both relationship memory and account creation value are demonstrated.
42. As a demo audience member, I want the destination account to visibly appear after the webhook, so that the pipeline-generation claim feels concrete.
43. As a developer, I want one end-to-end test that proves the full signal-to-action loop, so that the system's value is validated beyond unit coverage.
44. As a future integrator, I want the CRM and draft store behind interfaces, so that Airtable can later be swapped for HubSpot, Salesforce, or Gmail-backed experiences.
45. As a platform architect, I want one monolithic deployable app with modular internals, so that the first version is fast to build without collapsing boundaries.
46. As a maintainer, I want a clear demo runbook in the repo, so that the prototype can be operated by someone other than the original builder.
47. As a preview operator, I want manual deploys instead of automatic Git-driven deploys, so that the public demo environment changes only when intentionally promoted.
48. As a developer, I want model configuration to be environment-driven, so that preview-model churn does not require code changes.
49. As a seller, I want the CTA type chosen predictably based on relationship context, so that the ask is relevant but still controlled.
50. As an executive stakeholder, I want the prototype to clearly show that CrustData-style signals can autonomously create pipeline-ready action, so that the product story moves beyond "data provider" into "automation infrastructure."

## Implementation Decisions

- The prototype is centered on a single event type, `job_change`, with one primary hero scenario: a known contact moves to a net-new company.
- The system uses a normalized internal event schema as the stable contract. Raw CrustData-like webhook payloads are treated as external adapter inputs.
- The workflow is asynchronous from the perspective of the webhook ingress. The API validates and persists the event, returns `202 Accepted`, and dispatches execution to an internal runner.
- CRM state mutation is deterministic. The system does not allow the language model to decide record matching or business-state transitions.
- The business-facing CRM surface is Airtable with three conceptual entities: contacts, accounts, and an activity log.
- A contact can be updated or created provisionally when enough identity confidence exists. Ambiguous matches never silently mutate an existing record.
- A new destination account is created automatically when a champion moves to a company not already represented in the CRM surface.
- The workflow uses exact, auditable matching order for both contacts and accounts. Fuzzy matching is intentionally excluded from v1.
- The latest draft is surfaced on the contact record, but full draft history is append-only in the control-plane persistence layer.
- The system keeps long-lived CRM state separate from per-event execution state. Business UI and operational control plane are distinct responsibilities.
- The control plane stores raw events, normalized events, workflow runs, artifacts, and replay metadata. Local development uses SQLite; the hosted preview uses Railway-managed Postgres.
- The preview deployment remains a single FastAPI service with one process and one replica. The architecture is queue-shaped but executed in-process for v1.
- A lightweight recovery poller continuously watches for stuck or pending runs and resumes them from the first incomplete step when possible.
- Side-effecting steps are required to be independently idempotent so replay and recovery remain safe.
- The system uses Airtable in the hosted preview and can use a fake CRM adapter in local testing and offline development.
- The fake CRM preserves the relational business model rather than acting like an opaque key-value store.
- The model integration uses Gemini through the Gemini Developer API and the official Python SDK, wrapped behind a generic LLM interface.
- The preferred model path is configuration-driven with `gemini-3-flash-preview` as the default and `gemini-2.5-flash` as a backup model before deterministic fallback.
- Draft generation uses one-shot structured JSON output with internal application validation after provider-side schema enforcement.
- Draft quality is controlled by a separate message-policy layer that checks banned phrases, required facts, CTA/tone rules, and safety constraints.
- The fallback path produces the same draft artifact shape as the primary model path so downstream persistence and UI do not branch by draft origin.
- The model is responsible only for customer-facing wording. Confidence and business classifications are application-level, deterministic outputs.
- Optional enrichment can improve the prompt context, but it is bounded by a short timeout and never blocks the workflow from completing.
- The primary output is a single high-quality draft, not multiple variants.
- The CTA type comes from a small deterministic menu rather than being selected freely by the model.
- Sender identity is taken from CRM owner context, and the draft is written in the owner's voice.
- The preview environment is intentionally narrow: public webhook ingestion plus health endpoints only. Admin, replay, seeding, and reset actions stay off the public surface.
- Preview resets are privileged operator workflows that target a preview-specific namespace and require explicit confirmation.
- The preview uses manual CLI-driven deploys rather than Git-connected automatic promotion.
- The system uses explicit tenant and demo-environment tagging to isolate local and preview states even when they share higher-level infrastructure.
- The repo currently has no meaningful application code or test prior art beyond the specification artifact, so the PRD assumes greenfield implementation decisions rather than incremental modification of existing modules.

## Testing Decisions

- Good tests should validate external behavior and stable contracts, not implementation details. A good test proves what the system does when given a signal, not how many helper methods it called internally.
- Tests should prefer typed, business-level assertions such as "a provisional contact is created," "an activity summary is updated once per event," or "a fallback draft is produced when the model path fails."
- The workflow runner should be tested because it is a deep module that encapsulates dispatch, retries, stale-run recovery, and step progression behind a simple interface.
- The CRM resolution module should be tested heavily because matching and mutation correctness are central to trust in the system.
- The draft generation module should be tested for structured output handling, repair flow, backup model behavior, and deterministic fallback.
- The message policy module should be tested independently so content-safety and style rules are validated without needing a live model call.
- The webhook ingress module should be exercised mostly through integration tests because its value is in the end-to-end contract rather than isolated internal behavior.
- The operator module can be tested more lightly unless reset/replay logic becomes complex enough to justify deeper coverage.
- One end-to-end integration test is mandatory for the signal-to-action loop. It should simulate webhook ingestion, workflow execution, CRM mutation, and draft artifact creation.
- Idempotency behavior should be tested explicitly at the event level so redelivery of the same event does not create duplicate business-facing records.
- Prior art in the current codebase is effectively absent because the repository is greenfield. Test design should therefore follow the architecture in the spec rather than imitate existing local patterns.

## Out of Scope

- Live Salesforce integration
- Live HubSpot integration
- Gmail draft creation
- Automatic email sending
- Funding-round workflows
- Non-`job_change` watcher automations
- Approval UI or review queue
- Custom frontend dashboard
- Territory reassignment logic
- Multi-worker or horizontally scaled execution
- Exact fidelity guarantees to CrustData's private Watcher payload shape
- Production-grade multi-tenant administration beyond the prototype's lightweight tenant-aware core

## Further Notes

- The prototype's main job is to prove that watcher signals can become immediate, visible sales action without human orchestration.
- The most important demo artifact is the CRM mutation plus draft appearing in under 10 seconds.
- The most important engineering discipline is preserving a clean split between deterministic workflow state and model-generated language.
- The repo currently contains the implementation spec but is not a Git checkout, and local GitHub CLI authentication is invalid. As a result, this PRD is issue-ready Markdown but could not be submitted as a live GitHub issue from the current workspace state.
