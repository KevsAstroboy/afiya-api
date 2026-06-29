## Context

The existing workflow engine (`dynamic-workflow-engine` change) supports batch execution of parameterized workflows with LLM, function, condition, and HTTP step types. The Twilio webhook controller calls `engine.run()` to process incoming WhatsApp messages in batch mode. This works for post-payment notifications but not for interactive step-by-step patient data collection where each WhatsApp message corresponds to a single workflow step.

The user now requires: (1) patient data collection via WhatsApp using step-by-step conversation, (2) progressive Redis storage during collection, (3) single-point PostgreSQL/DynamoDB finalization, (4) Twilio replaced by WhatsApp Cloud API.

## Goals / Non-Goals

**Goals:**
- Replace Twilio with WhatsApp Cloud API (direct HTTP, no SDK)
- Add Redis `redis:7-alpine` via Docker Compose for conversational session storage
- Build `SessionManager` orchestrating WhatsApp conversation state machine (new → in-progress → complete)
- Add `llm_action` step type combining input validation + LLM message formatting
- Add `Validators` registry with 6 built-in validators, extensible without core changes
- Add `run_single_step()` to `WorkflowEngine` for WhatsApp conversational mode
- Keep existing engine, handlers, providers, repository layer, and 25 entity controllers intact
- Support both PostgreSQL and DynamoDB backends for session persistence compatibility

**Non-Goals:**
- Media (images, documents) via WhatsApp — text only
- WhatsApp template messages (content templates with buttons/lists)
- Multi-language support in validators
- WebSocket/SSE real-time notifications
- WhatsApp message status tracking (sent/delivered/read callbacks)

## Decisions

### D1: WhatsApp Cloud API via direct HTTP (no SDK)

**Choice:** Custom `WhatsAppService` using `httpx.AsyncClient` to call Meta Graph API endpoints directly. No third-party WhatsApp SDK.

**Rationale:** The WhatsApp Cloud API is a simple REST API with Bearer token auth. An SDK adds unnecessary dependency weight. The existing project already has `httpx` for the CinetPay service. Two endpoints to implement: webhook verification (GET) and message send (POST).

```python
# Send message
POST https://graph.facebook.com/v21.0/{phone_number_id}/messages
Authorization: Bearer {access_token}
{"messaging_product": "whatsapp", "to": "{wa_id}", "type": "text", "text": {"body": "Hello"}}

# Webhook verification  
GET /api/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=xxx&hub.challenge=xxx
→ return challenge value if token matches
```

### D2: Redis HASH per conversation

**Choice:** One Redis HASH key per WhatsApp conversation: `session:{wa_id}:context`. Fields map to collected data (e.g., `patient_nom`, `patient_prenom`, `state`, `current_step_id`). TTL defaults to 48h, resets on each write, overridable per workflow via `redis_ttl_hours`.

**Rationale:** HASH provides atomic field-level writes, avoids serialization overhead, and supports TTL natively. One key per conversation means no scans needed — O(1) lookup by wa_id. The TTL prevents stale sessions from accumulating.

**Alternatives considered:**
- *JSON value per key*: Requires full deserialization/serialization on every field write. Rejected.
- *PostgreSQL table for sessions*: Violates "Redis as progressive store, DB only at end" design. Rejected.
- *In-memory dict (no persistence)*: Lost on restart. Rejected.

### D3: SessionManager as orchestrator, not in the engine

**Choice:** `SessionManager` is a separate class that uses `WorkflowEngine.run_single_step()` as a component. It manages conversation state, Redis reads/writes, and triggers DB finalization. The engine remains a pure step executor.

**Rationale:** The engine should not know about WhatsApp, Redis, or conversation state — it's a workflow executor. The `SessionManager` is the WhatsApp-specific orchestrator that bridges the WhatsApp webhook, Redis, the engine, and the DB. This keeps concerns separated and both components independently testable.

### D4: run_single_step() returns a flat dict, not StepResult

**Choice:** `engine.run_single_step()` returns a dict: `{"status", "collected_key", "collected_value", "next_step_id", "whatsapp_reply"}`. The `SessionManager` never sees `StepResult`.

**Rationale:** The engine's internal `_execute_step()` returns `StepResult` (used by `run()`). `run_single_step()` transforms it to a flat dict so the `SessionManager` has a stable contract independent of engine internals. If the engine adds new fields to `StepResult`, the flat dict contract can be updated without breaking the `SessionManager`.

### D5: Validators registry with **kwargs pattern

**Choice:** Each validator receives `(raw: str, **config_kwargs)` where `config_kwargs` is the step's entire `config` dict. Validators pick what they need via keyword arguments, ignoring the rest.

```python
def nom(self, raw: str, **_) -> ValidationResult: ...
def expected_values(self, raw: str, expected_values=None, case_sensitive=False, value_map=None, **_) -> ValidationResult: ...
```

**Rationale:** This avoids coupling — a new validator can require new config keys without changing the handler dispatch. The `LLMActionHandler` passes the full step config, validators extract relevant params. Adding a validator is a one-line register + one method.

### D6: No DB migration for patients/biometrics tables

**Choice:** The `SessionManager._finalize()` writes to the database via the existing `DatabaseBackend` abstraction. For the patient collection use case, it delegates to the `db` interface (which already supports `insert`). No new SQLAlchemy entities needed — the `WorkflowDBInterface` handles the persistence.

**Rationale:** The user explicitly said "vous ne devez rien créer, ignorer" regarding patient tables. The `db` interface (`WorkflowDBInterface`) already has `find_one` — we'll add a generic `insert` method to support table-agnostic writes. This keeps the workflow engine compatible with both PostgreSQL and DynamoDB without entity-specific code.

## Risks / Trade-offs

- **WhatsApp API rate limits**: Meta enforces rate limits per phone number. Mitigation: `WhatsAppService` handles HTTP errors gracefully; the workflow engine's step failure routing handles transient errors.
- **Redis data loss**: If Redis crashes mid-conversation, session data is lost and the patient starts over. Mitigation: TTL provides auto-cleanup; the SessionManager detects missing sessions and restarts the workflow.
- **LLM latency**: Each step calls the LLM twice (once for validation, once for formatting). This adds ~1-3s per message. Mitigation: `run_single_step()` is async; the WhatsApp webhook responds after the LLM call completes (Meta's timeout is ~10s).
- **Validation false positives**: Validators may reject valid input. Mitigation: error messages are LLM-formatted to be helpful; configurable per step via `llm_prompt_error`.
