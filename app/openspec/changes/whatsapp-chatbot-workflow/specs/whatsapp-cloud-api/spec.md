## ADDED Requirements

### Requirement: Webhook verification via GET
The system SHALL expose a GET endpoint at `/api/webhook/whatsapp` that handles Meta's webhook verification by checking `hub.verify_token` against the configured `WHATSAPP_VERIFY_TOKEN` and returning the `hub.challenge` value if valid.

#### Scenario: Valid verification returns challenge
- **WHEN** GET `/api/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=correct&hub.challenge=abc123`
- **THEN** the response SHALL be HTTP 200 with body `abc123`

#### Scenario: Invalid verification returns 403
- **WHEN** GET `/api/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=wrong&hub.challenge=abc123`
- **THEN** the response SHALL be HTTP 403

### Requirement: Inbound message parsing via POST
The system SHALL parse Meta's JSON webhook payload to extract the sender's WhatsApp ID (`wa_id`), message text (`text.body`), message ID (`wamid`), and profile name (`profile.name`).

#### Scenario: Text message is parsed
- **WHEN** a valid Meta webhook JSON is received containing a text message
- **THEN** the system SHALL extract `wa_id`, `message_text`, `wamid`, and `profile_name`

#### Scenario: Non-text message is ignored gracefully
- **WHEN** a Meta webhook JSON is received containing a media message without text
- **THEN** the system SHALL extract `wa_id` with `message_text=None`

### Requirement: Outbound text message sending
The system SHALL send text messages via the WhatsApp Cloud API using the configured `WHATSAPP_PHONE_NUMBER_ID` and `WHATSAPP_ACCESS_TOKEN`.

#### Scenario: Text message sent successfully
- **WHEN** `send_text_message(to="2250712345678", body="Bonjour")` is called
- **THEN** a POST request SHALL be sent to `https://graph.facebook.com/v21.0/{phone_number_id}/messages` with the Bearer token and the message payload `{messaging_product: "whatsapp", to: "2250712345678", type: "text", text: {body: "Bonjour"}}`

#### Scenario: Invalid credentials return error
- **WHEN** the WhatsApp API returns an authentication error
- **THEN** the service SHALL log the error and raise an exception

### Requirement: Credentials configured via environment
All WhatsApp credentials SHALL be read from environment variables: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`, and `WHATSAPP_VERIFY_TOKEN`.

#### Scenario: Service uses config values
- **WHEN** `WhatsAppService` is instantiated
- **THEN** it SHALL read all four values from `Settings`
