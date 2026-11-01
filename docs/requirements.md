# Requirements and product scope (baseline v0.1)

## Vision

Create an importable and adaptable **accelerator**, not one fixed invoice product. A customer may add `registration` as a DocumentType, configure AI extraction fields (firstName, email, eventName), and route extracted data to their own Power Automate HTTP flow. The generic Document Core, inbox and audit/activity remain reusable without creating a Registration table.

## First use case: accounts payable invoice

- Input: Outlook attachment, SharePoint, manual upload or later other customer-specific Power Automate input flows.
- File enters through a standard RegisterDocument API. Registration stores original file in Blob and metadata in Dataverse.
- Known document type may be passed by source; otherwise AI classifies configured types.
- Azure OpenAI extracts baseline invoice fields, dynamic fields, category and a short AI summary. May use two calls for classification/supplier-specific instructions where appropriate.
- General instructions are customer-wide; field instructions are per document type; optional supplier natural-language instructions are applied only if supplier is unambiguously recognized.
- AI-only formatting instructions in V1, no general rules/regex validation engine. The platform still validates API/JSON schema and ensures safe edits.
- Supplier matching always operates against local Dataverse Supplier records (manual, ERP-synced, or human-approved new Supplier). Recipient/company/location matching operates against configured Company/CompanyLocation; do not create own companies automatically.
- Optional ERP supplier mapping and PO matching are Power Automate processing steps. If a configured required step fails, create a manual-review task; a disabled step is not a failure.
- Invoice lines are first-class Dataverse rows. Invoices without reliable lines are allowed.
- Human review uses the SAME document detail view as normal browsing; task deep-links focus the relevant panel. Fields editable before financial export; store revisions and audit actions.
- Distinguish document status, step execution, approval and transfer status. `Transferred` to ERP is not necessarily `Booked`.
- Notification/listener flows are fire-and-forget with tracked dispatch. Processing flows are blocking in workflow logic and callback asynchronously.
- Show Activity Feed and an attractive live-style dashboard; initial refresh can be polling. Real status must never be fabricated as live production data.

## Invoice-specific baseline columns

InvoiceNumber, InvoiceDate, DueDate, Supplier lookup, RecipientCompany lookup, RecipientLocation lookup, NetAmount (Money), TaxAmount (Money), GrossAmount (Money), Currency, PurchaseOrderNumber; ApprovalStatus, ERPExportStatus, ERPDocumentNumber, ERPExportedAt. InvoiceLine: LineNumber, Description, ArticleNumber, Quantity, Unit, UnitPrice (Money), NetAmount (Money), TaxRate, TaxAmount (Money), GrossAmount (Money), PurchaseOrderLineReference.

## Supplier / recipient specifics

- Supplier master: legal name, VAT, registration, address, contact fields, aliases and free-form AI instructions. Bank fields intentionally excluded from V1.
- Own Company: legal entity, VAT, address, internal code; CompanyLocation child rows with site address/code.
- AI can propose slight-name or address matches, but conflicting legal identifiers and mismatched recipients must be flagged rather than silently accepted. Automated acceptance of small differences is configurable. New supplier requires a human approval/edit opportunity.
- ERP-specific creditor number is not a Supplier master field; optional ERP mapping flow may store a customer-/company-specific reference later.

## Workflow defaults

AI Extraction -> Supplier Matching -> Recipient Matching -> [Duplicate Detection] -> [PO Matching] -> [Accounting] -> [Approval] -> [ERP Export] -> [Archiving]. Bracketed modules are optional. Enabled/required semantics are explicit in WorkflowStep. Business steps are Power Automate flows. Ordering is fixed per published workflow version; admin enables/disables predefined steps. New step types require development, not an end-user workflow editor.

## Explicitly deferred

Credit notes; delivery note 3-way matching or waiting for future documents; supplier bank accounts / bank change checks; complex approval hierarchies; sophisticated account allocations; dynamic document search index; designer for arbitrary workflows; production financial/tax compliance logic. DocumentType configuration itself must be available from V1, even if only invoice is fully processed.

## UX goals

Document list + personal/team task inbox + common document details + Activity Feed + dashboard/animated Processing Map + admin settings for AI, suppliers, recipients, document types and flows. Tasks focus relevant panel but do not use separate task-specific detail screens. Normal users cannot edit flow endpoint settings.

## Acceptance criteria for overall product (not first milestone)

- Add a `registration` document type and extract custom fields without changing Dataverse business schema.
- After supplier match failure, human creates/corrects supplier and resumes the same workflow.
- Configure an EventListener on `Document.Extracted` without blocking workflow.
- Replace demo ERP export FlowBinding with customer flow; stable input/output contract.
- Observe all events and user actions via Activity Feed without storing large payloads in Dataverse.
