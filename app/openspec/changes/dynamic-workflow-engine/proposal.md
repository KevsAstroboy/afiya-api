## Why

The telemedicine platform needs automated post-payment communication with patients via WhatsApp, orchestrated through a configurable workflow engine. Currently there is no workflow orchestration, no WhatsApp integration, no payment gateway integration, and the data layer is tightly coupled to PostgreSQL/SQLAlchemy — blocking future migration to DynamoDB or other backends.

## What Changes

- **New**: Dynamic workflow engine with DB-parameterized steps (LLM, function, condition, HTTP, WhatsApp) that orchestrates patient communication flows
- **New**: Repository abstraction layer (`RepositoryInterface[T]`) decoupling business logic from the database backend, with PostgreSQL adapter (wrapping existing SQLAlchemy code) and DynamoDB adapter
- **New**: WhatsApp integration via Twilio — send/receive messages, handle inbound webhooks
- **New**: CinetPay payment gateway integration — initiate payments, handle IPN callbacks, verify transactions
- **New**: LLM provider abstraction supporting Anthropic Claude and OpenAI GPT (extensible to any provider)
- **New**: FastAPI endpoints for workflow execution, WhatsApp webhook, and CinetPay webhook
- **Modified**: `core/config.py` — add `DB_BACKEND`, Twilio credentials, CinetPay credentials, LLM provider config
- **Modified**: `core/database.py` — introduce `DatabaseBackend` factory and `get_db_backend()` dependency
- **New**: Webhook-triggered workflow execution (WhatsApp inbound message or CinetPay payment confirmation starts the appropriate workflow)

## Capabilities

### New Capabilities

- `workflow-engine`: Core engine executing parameterized workflow steps (LLM, function, condition, HTTP, WhatsApp) with shared context dict, automatic routing, and full execution tracing. Steps are defined entirely in the database — no code changes needed to modify a workflow.
- `repository-abstraction`: Generic `RepositoryInterface[T]` protocol plus `DatabaseBackend` factory enabling PostgreSQL ↔ DynamoDB switching via a single config value. PostgreSQL adapter wraps existing SQLAlchemy repositories; DynamoDB adapter provides a NoSQL implementation.
- `whatsapp-integration`: Twilio-based WhatsApp messaging — inbound webhook handler creating conversations/messages, outbound message sending via workflow steps, and message status tracking.
- `payment-integration`: CinetPay payment gateway — payment initiation API, IPN callback webhook for payment confirmation, and transaction verification.
- `llm-provider-abstraction`: Pluggable LLM provider interface with Anthropic and OpenAI implementations, supporting prompt template variable substitution from the workflow context.

### Modified Capabilities

None — all existing capabilities retain their current behavior.

## Impact

- **Code**: New modules under `core/repository/`, `core/workflow/`, `services/twilio/`, `services/cinetpay/`, `controllers/api/workflow/`, `controllers/api/webhook/`, `models/workflow/`. Modifications to `core/config.py` and `core/database.py`. No changes to existing 25 entity CRUD layers (repositories remain functional as-is; abstraction wraps them progressively).
- **Dependencies**: `anthropic`, `openai`, `twilio`, `boto3` (DynamoDB), `httpx` (HTTP handler). CinetPay uses raw HTTP (no SDK). All except `openai` and `boto3` already in requirements or compatible.
- **Database**: New tables `workflow`, `workflow_step`, `workflow_execution`, `step_execution` for the workflow engine. No schema changes to existing tables.
- **API**: New endpoints `POST /api/workflow/execute`, `POST /api/webhook/twilio`, `POST /api/webhook/cinetpay`. Existing endpoints unchanged.
- **Configuration**: New env vars `DB_BACKEND`, `TWILIO_*`, `CINETPAY_*`, `LLM_PROVIDER`, `OPENAI_API_KEY`, `AWS_*` (for DynamoDB).
