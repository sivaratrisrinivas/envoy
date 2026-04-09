# Demo Runbook

## Primary Path
- Use the Railway preview deployment
- Verify `/healthz` and `/readyz`
- Open the preview Airtable namespace views
- Trigger the hero event
- Refresh the contact and account views
- Show the new account, updated contact, and drafted outreach

## Fallback Local Path
- Run `make bootstrap`
- Run `make seed`
- Run the app locally
- Trigger `make send-hero`
- Inspect the local fake CRM state or live Airtable local namespace

## Before/After Choreography
- Before: show the known contact at the old company and confirm the destination account is absent
- Trigger: send the hero event once
- After: show the contact moved, the new account created, the activity summary updated, and the draft ready

## Pre-demo Reset
- Reset the preview or local namespace explicitly
- Re-seed the baseline data
- Verify the hero contact has no new-account draft before the demo starts
