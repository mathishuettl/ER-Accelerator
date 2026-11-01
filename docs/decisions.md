# Architecture decision register

## Agreed decisions

| ID | Status | Decision |
|---|---|---|
| D-001 | Agreed | Deployable accelerator per customer, Power Platform Solution plus Azure resources |
| D-002 | Agreed | Generic Document + configurable DocumentType; Invoice has typed specialized projection and InvoiceLine |
| D-003 | Agreed | Dataverse holds structural/queryable data; Blob holds originals, dynamic fields, AI snapshots, large payloads |
| D-004 | Agreed | All monetary fields on Invoice/InvoiceLine use native Dataverse Currency/Money |
| D-005 | Agreed | Azure OpenAI is initial AI engine. Standard fields, custom fields, category, summary extracted; instructions editable |
| D-006 | Agreed | Simple prompt config, optional supplier-specific instructions with supplier recognized; avoid deep inheritance |
| D-007 | Agreed | Supplier matching against hub-owned Supplier; separate optional ERP mapping flow |
| D-008 | Agreed | Own Company and CompanyLocation master, invoice references both; address mismatch may require review |
| D-009 | Agreed | No supplier bank account model in first version |
| D-010 | Agreed | Azure Service Bus event bus; MessageOutbox for Events and Commands; Activity for user-readable history |
| D-011 | Agreed | Customer Processing Steps, EventListeners and Input Adapters use Power Automate; HTTP-flow registration is admin-owned |
| D-012 | Agreed | EventListener nonblocking; ProcessingStep returns standard async callback envelope, dynamic versioned step data |
| D-013 | Agreed | Central retries for transient failures; uncertain ERP effects never blindly retried |
| D-014 | Agreed | Predefined Processing Steps, enable/disable; custom new step by development; no UI workflow designer |
| D-015 | Agreed | Single document detail UI for all tasks, focused from inbox; editable fields with history |
| D-016 | Agreed | Demo ERP and example input/test flows part of accelerator; animated dashboard/Activity Feed desired |
| D-017 | Agreed | IngestionKey identifies retry of one source object; ContentHash identifies identical file content; ExternalReference removed |
| D-018 | Agreed | ExtractionRun has auto-number display, summary in both run and JSON; Document holds CurrentAISummary projection |
| D-019 | Agreed | No manual Dataverse table creation now; schema-first, automate provisioning later via Codex |

## Proposed technical choices to validate before coding

| ID | Status | Proposal / uncertainty |
|---|---|---|
| P-001 | Proposed | Azure Functions implements core APIs, state orchestration, dispatch, callbacks, outbox publication. Keep no customer business logic there. |
| P-002 | Proposed | Topic `document-events`, queue `processing-commands`; exact subscriptions and bus tier to verify for budget |
| P-003 | Proposed | Power Automate callback via authenticated Azure Function, request envelope v1.0 |
| P-004 | Proposed | Activity append-only for user-facing history; Dataverse native auditing for detailed sensitive field changes, scope/retention to decide |
| P-005 | Proposed | Invoice 1:1 with Document enforced through Dataverse alternate key on required lookup, subject to provisioning test |
| P-006 | Proposed | FieldDefinition and Category uniqueness by (DocumentType, key/code); choose choices and security details in DEV |
| P-007 | Proposed | Original file upload via streaming/staged Blob API, avoid large Power Automate JSON payloads |
| P-008 | Proposed | Direct Dataverse queries for Code App simple reads, API for stateful writes; verify Code Apps security/connection constraints |
| P-009 | Proposed | V1 activity dashboard polls; real-time push deferred |

## Explicitly open

- Exact tenant/environment/subscription/region, pricing, security role model, licensing and retention rules.
- Approval/exception policy on supplier name/address mismatch; human creation and whether manual confirmation is the default.
- Scope of an invoice correction after ERP transfer and association to an existing posting.
- Exact sample Power Automate flow callback and error status semantics for initial demo ERP.
- Versioned changes to active workflow definitions and to field definitions while documents are in progress.
- Security model for ProcessorTask assignments: direct SystemUser/Team lookups vs explicit application fields.
- Whether FI/ERP results need additional typed columns beyond status, reference and exported timestamp.
