## ADDED Requirements

### Requirement: Session is stored as a Redis HASH
The system SHALL store each WhatsApp conversation session as a single Redis HASH keyed by `session:{wa_id}:context` with a configurable TTL (default 48 hours).

#### Scenario: Session created on first message
- **WHEN** a WhatsApp message arrives from an unknown wa_id
- **THEN** a new Redis HASH SHALL be created with fields `wa_id`, `state="en_cours"`, `current_step_id`, and `last_message_at`

#### Scenario: Session TTL resets on each write
- **WHEN** a validated field is written to the session HASH
- **THEN** the TTL SHALL be extended to `redis_ttl_hours` from now

#### Scenario: Session TTL is configurable per workflow
- **WHEN** the workflow definition has `redis_ttl_hours=24`
- **THEN** the session TTL SHALL be set to 24 hours instead of the default 48

### Requirement: Validated fields are written to Redis atomically
The system SHALL write a field to the Redis HASH only after the step's validator confirms the input is valid. Invalid inputs SHALL NOT modify the HASH.

#### Scenario: Valid input stored in Redis
- **WHEN** the `nom` validator returns valid for input "Koné"
- **THEN** `patient_nom` SHALL be set to "KONÉ" in the Redis HASH

#### Scenario: Invalid input does not modify Redis
- **WHEN** the `nom` validator returns invalid for input "123"
- **THEN** no field SHALL be written to the Redis HASH and the current step SHALL remain unchanged

### Requirement: Session state machine (new → en_cours → complet)
The system SHALL track conversation state through three states: `new` (no session), `en_cours` (collecting data), and `complet` (all steps done, data finalized).

#### Scenario: Message to completed session returns info
- **WHEN** a message arrives for a session with `state=complet`
- **THEN** the system SHALL return a message indicating the dossier is complete with a reset instruction

#### Scenario: Reset keyword starts a new session
- **WHEN** a message contains a reset keyword (recommencer, restart, menu, 0, stop)
- **THEN** the existing session SHALL be deleted and a new one SHALL be created

### Requirement: Single-point database finalization
The system SHALL write collected data to the database exactly once, only when all workflow steps are complete and the `SessionManager._finalize()` method is called.

#### Scenario: Data written on workflow completion
- **WHEN** the last step of the workflow returns SUCCESS with `next_step_id=None`
- **THEN** `_finalize()` SHALL be called, writing all collected fields to the database

#### Scenario: Finalization failure preserves Redis state
- **WHEN** `_finalize()` raises an exception
- **THEN** the Redis session SHALL remain intact for retry and the state SHALL remain `en_cours`

### Requirement: SessionManager returns WhatsApp reply text
The system SHALL return a WhatsApp-ready text string from `handle_message()` that the webhook controller sends to the patient.

#### Scenario: Reply sent after successful step
- **WHEN** a step validates successfully and formats a reply via LLM
- **THEN** `handle_message()` SHALL return the formatted WhatsApp reply text

#### Scenario: Reply sent after failed step
- **WHEN** a step validation fails and formats an error message via LLM
- **THEN** `handle_message()` SHALL return the error message and the session state SHALL remain unchanged
