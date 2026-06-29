## Why

The telemedicine platform needs a WhatsApp chatbot that collects patient information step by step through conversational WhatsApp messages. Each response must be validated before storage, data stored progressively in Redis during the conversation, and saved to PostgreSQL/DynamoDB only once when the workflow completes. Twilio is being replaced by the WhatsApp Cloud API for direct Meta integration.

## What Changes

- **BREAKING**: Remove Twilio integration — delete `services/twilio/`, `controllers/api/twilio/`, all Twilio config fields, `twilio` dependency
- **New**: WhatsApp Cloud API service + webhook controller (Meta webhook verification + inbound message parsing + outbound text sending)
- **New**: Redis session store — HASH-based per-conversation state with configurable TTL
- **New**: `SessionManager` — orchestrates WhatsApp conversation flow: detect state, load Redis context, delegate single-step to engine, write validated fields, send reply
- **New**: Step type `llm_action` — validates user input against configurable validators, formats success/error WhatsApp reply via LLM, returns collected data
- **New**: `Validators` registry — 6 validators: nom, prenom, date_naissance, poids, taille, expected_values
- **New**: `LLMActionHandler` — composes validation + LLM formatting, returns `StepResult` with `whatsapp_reply`
- **Modified**: `WorkflowStep` — add `llm_prompt_success` and `llm_prompt_error` fields
- **Modified**: `WorkflowEngine` — add `run_single_step()` (executes one step by ID), add `llm_action` dispatch
- **New**: Redis in docker-compose + `redis` dependency + `REDIS_URL` config

## Capabilities

### New Capabilities

- `chatbot-session`: Redis-backed WhatsApp conversation session management with step-by-step data collection, configurable TTL, state machine (new/in-progress/complete), and single-point database finalization
- `llm-action-step`: Workflow step type combining input validation against configurable validators with LLM-powered success/error message formatting, returning `whatsapp_reply` text
- `whatsapp-cloud-api`: WhatsApp Cloud API integration — webhook verification (GET with challenge), inbound JSON message parsing, outbound text message sending via Graph API

### Modified Capabilities

- `workflow-engine`: `WorkflowEngine` gains `run_single_step()` method for WhatsApp conversational mode and dispatches `LLM_ACTION` step type via `LLMActionHandler`

## Impact

- **Removed**: `services/twilio/` (2 files), `controllers/api/twilio/` (1 file), `twilio==9.4.4` from requirements
- **New**: `services/whatsapp/` (2 files), `controllers/api/whatsapp/controller/` (1 file), `core/workflow/redis_session.py`, `core/workflow/session_manager.py`, `core/workflow/validators.py`, `core/workflow/handlers/llm_action_handler.py`
- **Modified**: `core/config.py`, `.env`, `requirements.txt`, `docker-compose.yml`, `core/workflow/types.py`, `core/workflow/engine.py`, `controllers/api/cinetpay/controller/cinetpay_controller.py`
- **Dependencies**: `redis>=5.0.0` (new), `twilio==9.4.4` (removed)
- **Infrastructure**: New Redis container in Docker Compose
- **No changes**: Providers, LLMHandler, FunctionHandler, ConditionHandler, HttpHandler, BusinessChecks, repository layer, PostgreSQL/DynamoDB backends, 25 entity controllers/services
