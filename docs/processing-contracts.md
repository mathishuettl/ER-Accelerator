# Power Automate contracts (version 1.0 draft)

## Philosophy

Every customer-specific business integration is a manually authored Power Automate HTTP-triggered flow. Admin registers a label and a **secret reference** to its trigger URL, plus contract version. There is NO implementation-type selector; the implementation is always Power Automate.

`EventListener`: launch on a configured event, do not wait for business success. Dispatch failures are visible, retried or alerted, but do not block main document workflow.

`ProcessingStep`: launch from Orchestrator; wait **logically** for asynchronous callback, not via persistent HTTP connection. Same step type has stable input and output schema for a given customer/contract version, even when actual ERP differs.

## Generic request envelope (ProcessingStep)

```json
{
  "schemaVersion":"1.0",
  "executionId":"exec-123",
  "documentId":"doc-456",
  "step":"ERP_SUPPLIER_MAPPING",
  "correlationId":"workflow-789",
  "data": {
    "supplierId":"supplier-1",
    "companyId":"company-1",
    "supplierName":"TechSupply GmbH",
    "vatNumber":"ATU12345678"
  }
}
```

The `data` object is step-specific and versioned. For custom document types, data can contain dynamically named fields. The administrator must see an example JSON request in the Code App and be able to copy it; preview must clearly distinguish dummy values from live data.

## Generic asynchronous callback

```json
{
  "schemaVersion":"1.0",
  "executionId":"exec-123",
  "success":true,
  "output":{"erpSupplierId":"700123"}
}
```

- Required: `schemaVersion`, `executionId`, `success` (boolean), `output` (object, possibly empty).
- `success: true`: validate step-specific output, commit result and advance.
- `success: false`: business-level unsuccessful result; for a required step create review task, for optional step follow defined skip/warning policy. Do not automatically retry valid business failures.
- Malformed/no callback or transport failures: centralized transient retry policy, then technical Failed. The special ERP export uncertain-outcome rule overrides automatic retry.
- Callback must be authenticated, correlated, idempotent and rejected on mismatched step/version. Do not trust arbitrary `documentId` in callback to write any document.
- Every step type declares a stable contract version, with example payload and JSON Schema where practical. `output` values must never silently change type between customer flows using same contract.

## Standard step-specific outputs (initial proposal)

| Step | Proposed output fields | Notes |
|---|---|---|
| AI Extraction | `extractionBlobKey`, `aiSummary`, `documentTypeCode`, `categoryCode` | Further dynamic fields in extraction snapshot |
| Supplier Matching | `supplierId` | Always local Dataverse supplier, never ERP creditor only |
| Recipient Matching | `companyId`, optional `companyLocationId` | Match against configured own entities |
| ERP Supplier Mapping | `erpSupplierId` | Optional customer-specific implementation |
| Duplicate Detection | `possibleDuplicateDocumentIds` | Optional |
| PO Matching | `matched`, optional mismatch details | Optional business logic |
| Accounting | `accountingDataBlobKey` | Optional, possibly line-level |
| Approval | `approved` | Approval is separate from a mere data correction |
| ERP Export | `erpDocumentNumber`, `transferConfirmed` | Transfer does not necessarily imply posting |
| Archiving | `archiveReference` | Optional |

These contracts are preliminary; do not provision/implement until schemas and required/optional fields have been reviewed against the first actual demo Power Automate flow.

## RegisterDocument: input interface (separate from flow callback)

- Request: authenticated source, stable `ingestionKey`, `fileName`, `contentType`, `source`, optional metadata and a stream/staged content reference. The JSON request is not expected to contain base64 PDFs.
- Success: return `documentId`, `isDuplicateIngestion` and registration status.
- Same ingestion key retry: same document; different receipt with identical file hash: separate receipt may be recorded and flagged for duplicate review.
- Sender/source identity and detailed metadata are included in Blob-side ingress snapshot, not a general ExternalReference Dataverse column.

## Standard errors (application API)

Return structured machine-readable error code with correlationId, user-safe message and retryability indicator. Distinguish invalid payload, unauthorized, conflict, transient dependency failures, callback-duplicate, unknown execution. Do not disclose sensitive internal IDs or secrets to unauthorized clients.

## Sample payloads

`examples/processing-step-request.json`, `examples/processing-step-callback.json`, `examples/document-register-request.json`, `examples/event-listener-request.json`.
