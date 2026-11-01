# Event bus and MessageOutbox contracts

## Vocabulary

**Status** = current state of a document, workflow or step. **Event** = an immutable fact that already occurred. **Command** = a request to perform an action. Events are observable by multiple listeners; commands are owned/handled once at the logical work level, even when the bus redelivers.

## Azure Service Bus design

- Topic: `document-events`, with consumer subscriptions for orchestrator and configured event listeners.
- Queue: `processing-commands`, with a core orchestration/dispatch consumer.
- All messages have unique stable `messageId`, a `correlationId`, `documentId` where available, `messageType`, `schemaVersion`, `occurredAt` and lightweight `data`/`payloadBlobKey`.
- Send from MessageOutbox publisher only after Dataverse commit. Record message outcome in MessageOutbox; consumers dedupe by messageId/executionId.
- Use dead-letter queues, alerts and a replay/retry procedure. An EventOutbox separate from MessageOutbox is explicitly **not** created.

## Proposed event vocabulary (draft)

| Event | Meaning |
|---|---|
| `Document.Received` | Document was registered |
| `Document.Classified` | DocumentType assigned |
| `Document.Extracted` | Extraction persisted |
| `Document.Confirmed` | Human confirmed document data |
| `Invoice.SupplierMatched` | Supplier linked to local Supplier |
| `Invoice.RecipientMatched` | Company/location linked |
| `Invoice.Approved` | Invoice approval decision recorded |
| `Invoice.Exported` | ERP transfer succeeded; does NOT mean posted unless confirmed |
| `Task.Completed` | A human task reached a terminal outcome |
| `ProcessingStep.Completed` | Generic step completed with result |
| `ProcessingStep.Failed` | Generic step failed definitively |

## Proposed command vocabulary (draft)

`Document.Extract`, `Supplier.Match`, `Recipient.Match`, `Invoice.ERPExport`, `Workflow.Advance`, `EventListener.Dispatch`.

Do not couple domain events to Dataverse table update trigger names; publish events only for actual meaningful state transitions. Do not allow arbitrary event listeners to advance the main workflow.

## Example event

See `examples/document-received-event.json`. Note that identifiers and references are examples; actual Dataverse GUIDs are generated at runtime. Event serialization is versioned; changing shape requires compatibility plan.
