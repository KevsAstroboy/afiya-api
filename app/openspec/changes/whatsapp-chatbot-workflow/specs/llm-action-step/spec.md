## ADDED Requirements

### Requirement: LLM_ACTION step type validates then formats
The system SHALL support a step type `llm_action` that: (1) validates the user's raw input against a configurable validator, (2) if valid, stores the cleaned value in the context and formats a success message via LLM, (3) if invalid, formats an error message via LLM without modifying the context.

#### Scenario: Successful validation stores value and formats message
- **WHEN** the `nom` validator returns `ValidationResult(valid=True, value="KONÉ")`
- **THEN** `context["patient_nom"]` SHALL be set to `"KONÉ"` and `llm_prompt_success` SHALL be used to generate the WhatsApp reply

#### Scenario: Failed validation formats error without storing
- **WHEN** the `nom` validator returns `ValidationResult(valid=False, reason="...")`
- **THEN** the context SHALL remain unchanged and `llm_prompt_error` SHALL be used to generate the error reply

#### Scenario: Missing validator passes transparently
- **WHEN** a step has no `validator` in its config
- **THEN** the raw input SHALL be accepted as-is and the step SHALL return SUCCESS

### Requirement: StepResult output contains WhatsApp reply
The `LLMActionHandler` SHALL return a `StepResult` whose `output` is a dict with keys `collected_key`, `collected_value`, and `whatsapp_reply`.

#### Scenario: Output includes collected data and reply
- **WHEN** a step successfully collects the patient's name
- **THEN** `output` SHALL contain `collected_key="patient_nom"`, `collected_value="KONÉ"`, and `whatsapp_reply` as a non-empty string

#### Scenario: Failure output includes error reply only
- **WHEN** a step fails validation
- **THEN** `output` SHALL contain `collected_key=None`, `collected_value=None`, and `whatsapp_reply` containing the error message

### Requirement: Validators are centrally registered
The system SHALL provide a `Validators` registry class where validators are registered by name. New validators SHALL be addable via `validators.register(name, fn)` without modifying the core.

#### Scenario: Registered validator is dispatched
- **WHEN** a step config has `validator="nom"` and `nom` is registered
- **THEN** the `nom` validator SHALL be called with the raw input and step config

#### Scenario: Unregistered validator returns error
- **WHEN** a step config references an unregistered validator name
- **THEN** the step SHALL return FAILURE with an error indicating the validator is not found

### Requirement: Validators receive full step config via kwargs
Each validator function SHALL receive `(raw: str, **config_kwargs)` where `config_kwargs` contains the step's entire config dict. Validators SHALL extract only the parameters they need.

#### Scenario: Validator uses only relevant parameters
- **WHEN** `expected_values` validator is called with `raw="1"`, `expected_values=["1","2"]`, `value_map={"1":"masculin"}`, and extraneous keys like `validator="expected_values"`, `context_target="..."`
- **THEN** the validator SHALL ignore extraneous keys and use only `expected_values` and `value_map`
