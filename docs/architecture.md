# System architecture (baseline v0.1)

## Components

| Component | Ownership |
|---|---|
| Power Apps Code App | UI: documents, task inbox, field edits, admin and dashboard |
| Dataverse | Typed business rows, config, workflow state, tasks, Activity, MessageOutbox |
| Azure Blob Storage | Original PDFs, extracted/custom JSON, revisions, large snapshots and event details |
| Azure Service Bus | `document-events` topic for published facts; `processing-commands` queue for work requests |
| Azure Functions | Core API, registration, orchestrator, dispatch, callback, outbox publisher, secure access |
| Power Automate | Every customer-specific input, Processing Step and Event Listener |
| Azure OpenAI | AI extraction, classification, categories and matching via Processing Flows |
| Azure Key Vault | Secrets / restricted endpoint configuration |

## End-to-end

1. A manually created Power Automate input flow receives an attachment or upload.
2. It calls an authenticated `RegisterDocument` API with a stable `ingestionKey` and file content/reference.
3. Core saves original bytes to Blob, computes SHA-256, writes Document/Activity/MessageOutbox in an atomic Dataverse changeset. Orphan blob cleanup/reconciliation must handle cross-system failure.
4. Outbox publisher sends `Document.Received` to Service Bus topic. Consumer is idempotent; no on-bus business state.
5. Orchestrator resolves DocumentType and active workflow version, creates WorkflowInstance/StepExecution and publishes processing command.
6. Dispatcher resolves configured FlowBinding, creates step-specific JSON from current data, stores full input snapshot in Blob and calls the secured HTTP Power Automate trigger.
7. Processing flow performs its task and POSTs a standard callback with matching executionId. The HTTP request must not stay open for long-running work.
8. Callback validates identity, executionId, contract version and expected step; persists output snapshot, state and activity+outbox in a consistent write.
9. Success advances next enabled step; business failure creates ProcessingTask if step required, or applies a documented optional-step policy. A human completes a task in the same document screen and workflow resumes.
10. EventListeners are dispatch-only and cannot change the main workflow state via a missing callback.

## Inbox

No independent Inbox table. Document lists read Document+Invoice; personal/team inbox reads ProcessingTask. Deep links use documentId + taskId + focusTarget; one shared edit form. Edits are versioned, audited, and may invalidate downstream checks. Already-transferred invoice corrections require a controlled path; no hidden ERP rebilling.

## Data segregation

- Dataverse: durable work state and queryable core fields.
- Blob: potentially large and changeable JSON and files. Treat blobs as private, versioned/immutable snapshots where appropriate. Store only blob keys/references in Dataverse.
- Message bus: minimal message headers/IDs and blob references, not PDF contents.
- Security: Entra authentication, API authorization, least-privilege managed identities, private containers. Do not expose Key Vault secret/flow URL to browser.

## Reliability design

- Dataverse record + Activity + MessageOutbox are one atomic Dataverse change set. Blob write is outside this transaction; use idempotent registration and orphan cleanup.
- Unique IngestionKey prevents duplicate registration attempts for same source object. ContentHash identifies identical files, but different receipts with same bytes need not be discarded automatically.
- Publisher retries pending MessageOutbox rows with stable MessageId; make downstream consumers idempotent anyway. Message kind distinguishes Events and Commands.
- Callback is accepted once per executionId and must not advance a completed/superseded step. Use optimistic concurrency or equivalent atomic state transition.
- Dispatcher timeout does NOT imply the downstream ERP action failed. Non-idempotent/uncertain ERP export -> manual investigation or reliable status lookup, never blind repost.
- Workflows snapshot their definition/version at start; new config versions do not rewrite running instances.
- Central retry policy for transient failures, no per-flow retry UI in MVP.

## ALM / packaging

Git source -> repeatable Dataverse metadata provisioning in DEV -> add components to named Power Platform solution -> Code App build/publish into that solution -> solution export/import to customers. Azure IaC deployed separately per tenant/subscription. Automate deployments; credentials and cloud IDs are environment-specific. Do not treat Microsoft-managed code app deployment as conventional source control integration.

## Technical review items (not implemented by this spec)

1. Validate full Code Apps connector and direct Dataverse behavior in target environment.
2. Choose how Power Automate HTTPS trigger is secured (Entra token permissions/region); store URL in Key Vault; verify callback auth.
3. Determine lowest-cost Azure Service Bus tier satisfying required topics, subscriptions and duplicate handling.
4. Determine blob retention/compliance for accounting documents in target jurisdiction.
5. Build a minimal real end-to-end test to verify Dataverse atomic changeset plus sender recovery.
6. Define source-independent, safely retryable original-file upload contract (stream vs staged reference).
