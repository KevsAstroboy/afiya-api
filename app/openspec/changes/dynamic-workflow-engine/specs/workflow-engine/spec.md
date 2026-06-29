## ADDED Requirements

### Requirement: Workflow definitions are stored in database
The system SHALL store workflow definitions in a `workflow` table and their steps in a `workflow_step` table, both fully parameterized. No workflow logic SHALL be hardcoded — changing step order, prompts, routing, or config MUST NOT require code changes.

#### Scenario: Retrieve workflow with steps
- **WHEN** a workflow is queried by its ID
- **THEN** the system returns the workflow metadata and all associated steps ordered by `step_order`

#### Scenario: Activate or deactivate a workflow
- **WHEN** a workflow's `is_active` flag is set to FALSE
- **THEN** the engine SHALL refuse to execute that workflow

### Requirement: Engine executes steps sequentially with shared context
The `WorkflowEngine` SHALL execute steps in order, starting from the first step (`step_order = 1`), maintaining a shared context dictionary that each step can read from and contribute to.

#### Scenario: Context is shared across steps
- **WHEN** step A injects `step_a_output` into the context
- **THEN** step B SHALL be able to read `step_a_output` from the context

#### Scenario: Context is initialized with input_data
- **WHEN** the engine starts with `input_data = {"telephone": "0700000000"}`
- **THEN** the context SHALL contain `input_telephone = "0700000000"` from the start

### Requirement: Engine routes based on step success or failure
After each step executes, the engine SHALL route to `on_success_step_id` if the step status is SUCCESS or to `on_failure_step_id` if the status is FAILURE. If the referenced step ID does not exist, the engine SHALL terminate the workflow.

#### Scenario: Successful step routes to next step
- **WHEN** step 1 completes with status SUCCESS and has `on_success_step_id = step-2`
- **THEN** the engine SHALL execute step 2 next

#### Scenario: Failed step routes to failure branch
- **WHEN** step 1 completes with status FAILURE and has `on_failure_step_id = step-error`
- **THEN** the engine SHALL execute step-error next

#### Scenario: Terminal step ends the workflow
- **WHEN** a step has `is_terminal = TRUE`
- **THEN** the engine SHALL stop execution regardless of success/failure routing

### Requirement: Engine supports LLM step type
The engine SHALL support a `step_type = 'llm'` that calls an LLM provider, substitutes context variables in the prompt template using `{key}` syntax, and injects the response into the context as `step_{name}_output`.

#### Scenario: LLM step with prompt variable substitution
- **WHEN** a step has `llm_prompt = "Hello {input_name}"` and context contains `input_name = "Amadou"`
- **THEN** the LLM SHALL receive the prompt "Hello Amadou"

#### Scenario: LLM step output is cast to float when numeric
- **WHEN** the LLM returns the text "0.85"
- **THEN** `step_{name}_output` in the context SHALL be the float `0.85`

#### Scenario: LLM step with missing prompt variable fails
- **WHEN** a prompt references `{missing_key}` that does not exist in the context
- **THEN** the step SHALL return status FAILURE with error message indicating the missing variable

### Requirement: Engine supports function step type
The engine SHALL support a `step_type = 'function'` that dispatches to registered business check functions by name, passing the context and step config as arguments.

#### Scenario: Function check returns passed
- **WHEN** a function `check_record_exists` finds a matching record
- **THEN** the step SHALL return status SUCCESS with output containing the check reason and data

#### Scenario: Function check returns failed
- **WHEN** a function `check_payment_status` finds the payment status does not match
- **THEN** the step SHALL return status FAILURE with output containing the failure reason

#### Scenario: Unregistered function name
- **WHEN** a step references a `function_name` not present in the registry
- **THEN** the step SHALL return status FAILURE with an appropriate error message

### Requirement: Engine supports condition step type
The engine SHALL support a `step_type = 'condition'` that evaluates a logical expression on context values using operators (`==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `not_in`).

#### Scenario: Condition evaluates to true
- **WHEN** `left = "step_scoring_output"` (value 0.85), operator `>=`, `right = 0.7`
- **THEN** the step SHALL return status SUCCESS

#### Scenario: Condition evaluates to false
- **WHEN** `left = "step_scoring_output"` (value 0.4), operator `>=`, `right = 0.7`
- **THEN** the step SHALL return status FAILURE

#### Scenario: Condition key missing from context
- **WHEN** the `left` key does not exist in the context
- **THEN** the step SHALL return status FAILURE with error indicating the missing key

### Requirement: Engine supports HTTP step type
The engine SHALL support a `step_type = 'http'` that makes an HTTP request based on config parameters (URL, method, headers, body), substitutes context variables in all templated fields, and evaluates success based on the response status code.

#### Scenario: HTTP call succeeds
- **WHEN** the HTTP request returns a status code matching `success_status` in config
- **THEN** the step SHALL return status SUCCESS with the response body in output

#### Scenario: HTTP call fails
- **WHEN** the HTTP request returns a non-matching status code or raises a network error
- **THEN** the step SHALL return status FAILURE with the error details

#### Scenario: HTTP call with context variable substitution in body
- **WHEN** `body_template = 'To={input_telephone}&Body={step_msg_output}'`
- **THEN** the HTTP request body SHALL contain the substituted values

### Requirement: Business checks inject records into context
Business check functions (`check_record_exists`, `check_payment_status`) SHALL inject fetched database records into the context using the naming convention `db_{table}_record`.

#### Scenario: check_record_exists injects record
- **WHEN** `check_record_exists` finds a user in the `clients` table
- **THEN** `db_clients_record` SHALL be available in the context with the full record

#### Scenario: check_payment_status injects record
- **WHEN** `check_payment_status` finds a confirmed payment
- **THEN** `db_payment_record` SHALL be available in the context with payment details

### Requirement: Engine traces every execution
Every workflow execution SHALL be recorded in `workflow_execution` and every step execution in `step_execution`, including start time, end time, status, input data, output data, LLM responses, and error messages.

#### Scenario: Execution trace includes all steps
- **WHEN** a workflow with 3 steps completes
- **THEN** 1 `workflow_execution` record and 3 `step_execution` records SHALL be persisted

#### Scenario: Failed step trace includes error
- **WHEN** a step fails with an error
- **THEN** the `step_execution` record SHALL contain the error message and the step status SHALL be 'failure'

### Requirement: New business checks can be registered without modifying the engine
The engine SHALL expose a `register_check(name, callable)` method allowing new business logic to be added at runtime without touching the engine core.

#### Scenario: Register a custom check
- **WHEN** a new function is registered via `engine.register_check("my_check", my_fn)`
- **THEN** a workflow step referencing `function_name = "my_check"` SHALL dispatch to that function

### Requirement: New step-type handlers can be added without modifying the engine core
Adding a new step type (e.g., `webhook`, `database`) SHALL require only creating a new Handler class and registering it, without modifying the engine's `_execute_step` dispatch logic.

#### Scenario: Add a new handler type
- **WHEN** a `DatabaseHandler` is created and registered with the engine
- **THEN** steps with `step_type = 'database'` SHALL be dispatched to that handler
