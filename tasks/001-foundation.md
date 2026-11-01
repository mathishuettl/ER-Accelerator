# Task 001 - Foundation and one vertical registration slice

## Goal

Prove deployment and cross-service messaging using one example PDF: Power Automate demo input -> protected RegisterDocument API -> Blob + Dataverse -> atomic MessageOutbox -> Service Bus -> Activity/logging -> minimal Power Apps Code App document list. **No** extraction, matching, real ERP calls or production data.

## Inputs / prerequisites (user must provide or explicitly authorize)

- Dev Power Platform environment with Dataverse enabled; security/identity rights to create solution components.
- Dev Azure subscription + resource group/region, budget and resource provisioning permission.
- A non-sensitive example PDF or generated sample file.
- Preferred publisher prefix/solution unique name (draft `iac`), test accounts/service principal.

## Deliverables

1. Repo folder structure: `src/code-app`, `src/functions`, `infra/bicep`, `infra/dataverse`, `tests`, `flows/demo-input`.
2. Infrastructure-as-code for Azure storage, service bus topic+queue, Key Vault, Function App and minimum monitoring. Parameters; no hardcoded tenant IDs or secrets.
3. Repeatable Dataverse metadata provisioner that only creates the **minimum** objects for this slice (Document, DocumentType, Activity, MessageOutbox), with schema validation and solution membership. Full `spec/data-model.yaml` remains the target model.
4. Secure RegisterDocument API and idempotent receipt path; compute file SHA-256 and a separate stable ingestion key.
5. Dataverse write operation that registers Document, Activity and MessageOutbox atomically after successful blob staging; retry/reconciliation for cross-system partial failures.
6. Outbox dispatcher + one Service Bus receiver; acknowledgements and idempotency tests.
7. Demo-input Power Automate template/manual setup instructions sending one PDF to RegisterDocument (real HTTP URL configured by admin, not committed).
8. Minimal Power Apps Code App document list with ID, filename, status, receivedAt and Activity viewer. Verify publishing into named solution in DEV.
9. Automated tests, smoke-test script and deployment/cleanup commands.
10. Updated README and concrete instructions for customer import/connection variable placeholders.

## Acceptance criteria

- Two calls with same ingestion key do not create duplicate Document rows; API returns same documentId.
- Two receipts with different ingestion keys but same PDF produce two receipts with same content SHA-256, flagged as possible duplicate (not silently dropped).
- Failed Service Bus publish leaves MessageOutbox Pending/Failed and republish works using same MessageId.
- Redelivery does not create repeated workflow effects or double Activity entries for same logical event.
- Blob upload succeeds but Dataverse fails: reconciler can detect/clean up orphan blob; no false "registered" result.
- Document in DEV Dataverse appears in the Code App with at least one Activity item.
- All resources provision from scripts; no manual schema editing needed. CLI/auth permissions are prerequisites not guessed by scripts.
- No secrets or HTTP trigger URLs stored in Git or in browser-facing Dataverse fields.
- `schemaVersion`, base JSON contracts and YAML lint/validation tests pass.

## Suggested implementation order

A. Set up repo, local schema validator and dry-run infrastructure plan.
B. Provision DEV resources and minimum Dataverse tables after user provides identifiers.
C. Implement RegisterDocument with mocked Dataverse/Blob clients in tests, then real DEV integration.
D. Implement Outbox publisher/consumer and idempotency tests.
E. Add demo Power Automate input flow and minimal Code App view.
F. Record evidence: deploy commands, logs, screenshot or test output and cleanup instructions.

## Do not do in task 001

Do not create all 19 tables automatically before verifying metadata provisioning; do not add live Azure OpenAI extraction, supplier matching, ERP export, bank storage, complex workflow designer or final fancy live animation. Foundation may contain stubs/interfaces for later features, not invented implementations.
