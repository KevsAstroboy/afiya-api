## ADDED Requirements

### Requirement: Inbound WhatsApp webhook handler
The system SHALL expose a `POST /api/webhook/twilio` endpoint that receives incoming WhatsApp messages from Twilio, validates the request signature, creates or updates a `conversation` and `message` record, and triggers the appropriate workflow.

#### Scenario: New conversation from first WhatsApp message
- **WHEN** a WhatsApp message is received from an unknown phone number
- **THEN** the system SHALL create a new `conversation` record linked to a new or existing `user`, create a `message` record with the WhatsApp message content, and trigger the onboarding workflow

#### Scenario: Existing conversation receives new message
- **WHEN** a WhatsApp message is received from a known phone number with an active conversation
- **THEN** the system SHALL append a new `message` record to the existing conversation

#### Scenario: Twilio request signature validation fails
- **WHEN** the `X-Twilio-Signature` header does not match the computed signature
- **THEN** the system SHALL return HTTP 403 and SHALL NOT process the message

### Requirement: Outbound WhatsApp message via HTTP workflow step
The system SHALL allow sending WhatsApp messages through a workflow HTTP step configured to call the Twilio Messages API, with the recipient phone number, message body, and credentials substituted from the workflow context.

#### Scenario: WhatsApp message sent from workflow context
- **WHEN** an HTTP step is configured with Twilio endpoint, auth, and body template `To=whatsapp:{input_telephone}&Body={step_llm_output}`
- **THEN** the system SHALL call the Twilio API and store the returned `message_sid` as `whatsapp_message_id` in the message record

#### Scenario: WhatsApp send fails
- **WHEN** Twilio returns an error (e.g., invalid phone number)
- **THEN** the HTTP step SHALL return status FAILURE and the error details SHALL be logged

### Requirement: Twilio service for WhatsApp operations
The system SHALL provide a `TwilioService` class encapsulating Twilio client initialization, message sending, webhook signature validation, and phone number formatting.

#### Scenario: TwilioService formats international number
- **WHEN** `TwilioService.format_whatsapp_number("0700000000")` is called
- **THEN** it SHALL return `whatsapp:+2370700000000` (using the configured country code prefix)

#### Scenario: TwilioService sends a message
- **WHEN** `TwilioService.send_message(to="whatsapp:+2370700000000", body="Hello")` is called
- **THEN** the Twilio client SHALL be invoked and the message SID SHALL be returned

### Requirement: Message delivery status tracking
The system SHALL store Twilio message status updates (sent, delivered, read, failed) by updating the corresponding `message` record's `statut_livraison_id` field.

#### Scenario: Status callback updates message status
- **WHEN** Twilio sends a status callback webhook indicating "delivered"
- **THEN** the system SHALL update the `message` record's `statut_livraison_id` to the corresponding status code

### Requirement: WhatsApp message content stored in message table
Every WhatsApp message (inbound or outbound) SHALL be stored in the `message` table with the `whatsapp_message_id`, `contenu`, `type_contenu`, `sender_user_id` or `receiver_user_id`, and timestamps.

#### Scenario: Inbound text message stored
- **WHEN** a WhatsApp text message is received
- **THEN** a `message` record SHALL be created with `type_contenu = 'text'`, `emetteur_id = PATIENT`, and the correct `conversation_id`

#### Scenario: Outbound message stored with Twilio SID
- **WHEN** a WhatsApp message is sent via Twilio
- **THEN** the resulting `message` record SHALL contain the `whatsapp_message_id` from Twilio's response
