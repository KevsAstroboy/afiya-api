## ADDED Requirements

### Requirement: Payment initiation via CinetPay
The system SHALL provide a `CinetPayService` that initiates a payment on the CinetPay gateway and persists the payment record in the `paiement` table with request and response payloads.

#### Scenario: Payment initiated successfully
- **WHEN** `CinetPayService.initiate_payment(consultation_id, amount, currency)` is called
- **THEN** the system SHALL call CinetPay's payment initialization endpoint, store the `request_payload` and `response_payload` in the database, and return the CinetPay payment URL and `transaction_id`

#### Scenario: Payment initiation fails
- **WHEN** CinetPay returns an error response
- **THEN** the system SHALL store the error details in `paiement_metadata` and raise a `BusinessException`

### Requirement: IPN callback webhook for payment confirmation
The system SHALL expose a `POST /api/webhook/cinetpay` endpoint that receives CinetPay's Instant Payment Notification (IPN), validates the payment, updates the `paiement` record's status, and triggers the post-payment workflow.

#### Scenario: Valid IPN confirms payment
- **WHEN** a valid IPN is received with `status = 'ACCEPTED'`
- **THEN** the system SHALL update the `paiement` record's `statut_paiement_id` to the confirmed status, store the IPN payload as `verify_payload`, set `date_validation`, and trigger the post-payment workflow

#### Scenario: IPN indicates payment failed
- **WHEN** an IPN is received with `status = 'REFUSED'`
- **THEN** the system SHALL update the `paiement` status to failure and SHALL NOT trigger the workflow

#### Scenario: IPN for non-existent transaction
- **WHEN** an IPN references a `transaction_id` not found in the database
- **THEN** the system SHALL return HTTP 404

#### Scenario: IPN signature verification fails
- **WHEN** the IPN payload's signature does not match
- **THEN** the system SHALL return HTTP 403 and SHALL NOT update the payment

### Requirement: Payment status verification
The system SHALL support verifying a payment's status by calling CinetPay's check endpoint, using the stored `transaction_id`.

#### Scenario: Verify confirmed payment
- **WHEN** `CinetPayService.verify_payment(transaction_id)` is called for a confirmed payment
- **THEN** the system SHALL return the payment status from CinetPay and update the local `paiement` record if changed

### Requirement: Payment record stores full audit trail
Every `paiement` record SHALL store the raw request payload sent to CinetPay (`request_payload`), the raw response from CinetPay (`response_payload`), the IPN verification payload (`verify_payload`), and structured metadata (`paiement_metadata`).

#### Scenario: Complete audit trail for a payment
- **WHEN** a payment goes through initiation → IPN confirmation
- **THEN** all three payloads (`request_payload`, `response_payload`, `verify_payload`) SHALL be non-null and stored as-is for audit purposes

### Requirement: Workflow trigger on payment confirmation
When a payment is confirmed via IPN callback, the system SHALL trigger the configured post-payment workflow by calling `WorkflowEngine.run()` with the relevant input data (patient info, payment details, consultation context).

#### Scenario: Post-payment workflow triggered on confirmation
- **WHEN** CinetPay IPN confirms a payment
- **THEN** the system SHALL call `WorkflowEngine.run(workflow_id, {"input_telephone": "...", "input_transaction_id": "...", "input_consultation_id": "..."})`

#### Scenario: Payment confirmation with missing workflow configuration
- **WHEN** a payment is confirmed but no post-payment workflow is configured
- **THEN** the system SHALL log a warning and SHALL NOT raise an error

### Requirement: CinetPay credentials configured via environment
All CinetPay credentials (site ID, API key, secret key, endpoints) SHALL be read from environment variables or the `.env` file via the `Settings` class, never hardcoded.

#### Scenario: CinetPay service uses config values
- **WHEN** `CinetPayService` is instantiated
- **THEN** it SHALL read `CINETPAY_SITE_ID`, `CINETPAY_API_KEY`, `CINETPAY_SECRET_KEY`, `CINETPAY_INIT_ENDPOINT`, and `CINETPAY_CHECK_ENDPOINT` from `Settings`
