# Invoice Automation Accelerator - Codex handover v0.1

Status: **architecture baseline / implementation draft**, not deployed and not production-ready.

This repository skeleton turns the agreed discovery sessions into developer-readable requirements and contracts. It does **not** contain a working app, a Power Platform Solution export, or real Azure credentials. Its goal is to give Codex a precise starting point and a testable first task.

## Product in one paragraph

A reusable, customer-deployed Power Platform accelerator: a generic document core with configurable document types, AI extraction fields and categories; an invoice-specific structured projection; an event-driven workflow orchestrator; Power Automate as the *only* customer-specific processing/integration implementation; a Power Apps code app for document overview, tasks, editing, activity and animated monitoring; Azure Service Bus, Azure Functions, Dataverse, Blob Storage and Azure OpenAI as core infrastructure. Customers can add a type such as `registration` without a new Dataverse business table and send extracted fields through their own Power Automate flow.

## Reading order

1. `docs/requirements.md` - scope, workflows, what is excluded
2. `docs/architecture.md` - components, flows, ownership and safety constraints
3. `spec/data-model.yaml` - proposed Dataverse schema (19 tables, 181 proposed fields)
4. `docs/events.md` and `docs/processing-contracts.md` - event bus and flow contracts
5. `docs/decisions.md` - decisions, assumptions and intentionally open points
6. `tasks/001-foundation.md` - first implementable task with acceptance criteria
7. `AGENTS.md` - instructions Codex should follow

## First useful milestone

Provision a development-only foundation; register one example PDF through a demo input adapter, see the document in Dataverse and in a minimal code-app document list, and see an `Activity` item for registration. All components must be reproducible; the project is not done when a resource was manually created once.

## Deployment approach

- Dataverse tables, choices, relationships, app and flows -> Power Platform Solution, eventually imported into each customer's environment.
- Azure Functions, Service Bus, Blob Storage, Key Vault and monitoring -> repeatable Azure IaC (Bicep), Azure OpenAI deployment/availability configured per environment.
- Environment-specific settings -> connection references, environment variables, secret references and identity configuration.
- Source of truth for code -> Git. Actual Solution is a build/deployment artifact.

## This pack intentionally does not include

- Real credentials, Power Automate HTTP trigger URLs, customer data or real PDFs.
- A working Dataverse provisioner, deployed cloud resources or verified tenant permissions.
- Automatic accounting, production tax checks, legal archive compliance, comprehensive approvals, bank account storage, credit notes or delivery-note workflows.

## Official documentation checked on 2026-11-01

- Dataverse table creation: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-definitions-using-web-api
- Dataverse atomic change sets: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/execute-batch-operations-using-web-api
- Alternate keys: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-alternate-keys-reference-records
- Code apps / solution deployment: https://learn.microsoft.com/en-us/power-apps/developer/code-apps/how-to/push-to-solution
- Service Bus delivery and idempotency: https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-message-loss-and-duplicates
- Power Automate HTTP trigger authorization: https://learn.microsoft.com/en-gb/power-automate/oauth-authentication?tabs=classic-designer
