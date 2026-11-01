# Codex operating instructions

You are implementing a reusable Microsoft Power Platform / Azure document processing accelerator. Read `README.md`, `docs/requirements.md`, `docs/architecture.md`, `spec/data-model.yaml`, `docs/processing-contracts.md`, `docs/events.md`, and `docs/decisions.md` before changing architecture.

## Non-negotiable decisions

- Generic `Document` core and configurable `DocumentType`. `Invoice` is an optional typed projection, not the universal document model.
- Keep standard invoice fields in Dataverse, with configurable AI descriptions. Keep dynamic fields and full AI snapshots in Blob Storage.
- Use Dataverse Money/Currency fields for all invoice amounts and invoice line prices/amounts.
- Supplier matching always resolves against Hub-owned `Supplier` records; optional ERP supplier lookup/mapping is a separate Power Automate processing step.
- All CUSTOMER-SPECIFIC processing steps, input adapters and event listeners are Power Automate flows. Azure Functions is allowed only for core APIs, orchestration, dispatch, callbacks, security and publication; do not move customer business logic to Functions.
- Azure Service Bus is the event bus. Dataverse `MessageOutbox` stores pending *Events and Commands* reliably. Business history is `Activity`, not Service Bus.
- HTTP Power Automate FlowBindings: `EventListener` does not block; `ProcessingStep` waits logically for an asynchronous, standard result (`executionId`, `success`, `output`). Do not hold long HTTP connections open.
- An administrator provisions flows manually and registers an endpoint, label and contract. No public end-user flow builder.
- One document-detail UI for all tasks, with deep-link/focus on the relevant field or panel. All pre-export extracted fields are editable and changes are historized.
- Keep changes aligned with the first vertical slice defined in `tasks/001-foundation.md`.

## Mandatory safety / operational constraints

- Work against a **development environment only**. Never provision cloud resources, deploy to an existing tenant, or access production without explicit environment identifiers and permission from the user.
- Never commit API keys, callback credentials, full HTTP trigger URLs, SAS tokens, customer documents or secrets. Store actual secrets in Key Vault and only secret references in Dataverse.
- Require authenticated callers and authorize actions at the API; app visibility is not an authorization boundary.
- Handle `RegisterDocument` retries by a stable ingestion key. Compute a separate file-content SHA-256 hash; never equate the two.
- All message handlers, callbacks and document updates must be idempotent. Prevent concurrent state advances and duplicate registrations.
- Do not retry uncertain non-idempotent ERP posting blindly. If the remote outcome is unknown, mark for review.
- Preserve original extraction data, current user-corrected state and revisions separately; never overwrite a confirmed edit silently.
- Do not assume machine-generated values are correct, especially supplier/recipient identities and financially consequential data.
- Verify current CLI commands, supportability, licensing and APIs against Microsoft Learn before execution; do not invent a PAC/Power Apps command.
- Use migrations / repeatable provisioning. If a proposed Dataverse feature is unsupported, note and propose a minimal alternative rather than silently changing the model.
- Do not expand scope into bank account tables, complex workflow editor, credit notes, or delivery-note matching in the first milestone.

## Working method

1. State the implementation slice and files to change.
2. Mark unresolved decisions in `docs/decisions.md`, do not assume they were agreed.
3. Generate repeatable scripts and tests before provisioning.
4. Validate YAML and JSON contracts automatically.
5. Show tests, assumptions, exact commands and resource-cost implications.
6. Report blockers; do not claim cloud resources were deployed unless actually verified.

## Expected first task

Implement `tasks/001-foundation.md` only. Target result: demo document registration -> Dataverse Document + Activity + MessageOutbox -> Service Bus event -> minimal document-list UI. AI extraction, real ERP posting and production permissions are out of scope.
