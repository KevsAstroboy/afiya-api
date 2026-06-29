## 1. Configuration & Dependencies

- [x] 1.1 Add new environment variables to `core/config.py`: `DB_BACKEND`, `LLM_PROVIDER`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `CINETPAY_SITE_ID`, `CINETPAY_API_KEY`, `CINETPAY_SECRET_KEY`, `CINETPAY_INIT_ENDPOINT`, `CINETPAY_CHECK_ENDPOINT`, `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- [x] 1.2 Add `openai`, `boto3`, `httpx` to `requirements.txt`
- [x] 1.3 Update `.env` with placeholder values for all new config variables

## 2. Repository Abstraction Layer

- [x] 2.1 Create `core/repository/interface.py` — define `RepositoryInterface[T]` ABC with methods: `create`, `get_by_id`, `get_all`, `update`, `delete`, `find_one`, `find_by`
- [x] 2.2 Create `core/repository/backends/postgresql.py` — implement `SqlAlchemyRepository[T]` generic CRUD using SQLAlchemy entity introspection (table name, columns, soft-delete auto-detection)
- [x] 2.3 Create `core/repository/backends/__init__.py` — export backend classes
- [x] 2.4 Create `core/database.py` additions — implement `DatabaseBackend` ABC, `PostgreSQLBackend(session)`, and `get_db_backend()` FastAPI dependency using `DB_BACKEND` config
- [x] 2.5 Create `core/repository/__init__.py` — public exports

## 3. Workflow Engine Core

- [x] 3.1 Create `core/workflow/types.py` — dataclasses: `StepType` enum (llm, function, condition, http), `StepStatus` enum (success, failure), `WorkflowStep`, `StepResult`, `CheckResult`
- [x] 3.2 Create `core/workflow/engine.py` — `WorkflowEngine` class: `run(workflow_id, input_data)`, `_execute_step(step, context)`, step routing logic, context enrichment (`step_{name}_output`)
- [x] 3.3 Create `core/workflow/handlers/llm_handler.py` — `LLMHandler` with prompt variable substitution via `format_map(context)`, auto-casting to float, error handling
- [x] 3.4 Create `core/workflow/handlers/function_handler.py` — `FunctionHandler` with registry (`register(name, fn)`), dispatches to functions by `function_name` from step config
- [x] 3.5 Create `core/workflow/handlers/condition_handler.py` — `ConditionHandler` with operators (`==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `not_in`), context value evaluation
- [x] 3.6 Create `core/workflow/handlers/http_handler.py` — `HttpHandler` with HTTP method, URL/header/body template substitution from context, basic auth support, status code validation
- [x] 3.7 Create `core/workflow/checks.py` — `BusinessChecks` class: `check_record_exists`, `check_fields_complete`, `check_payment_status` following provided spec with `db` interface injection
- [x] 3.8 Create `core/workflow/__init__.py` — public exports for all engine components

## 4. LLM Provider Abstraction

- [x] 4.1 Create `core/workflow/providers/base.py` — `LLMProvider` ABC with `async generate(prompt, model, max_tokens) -> str`
- [x] 4.2 Create `core/workflow/providers/anthropic.py` — `AnthropicProvider` wrapping `anthropic.Anthropic().messages.create()`
- [x] 4.3 Create `core/workflow/providers/openai.py` — `OpenAIProvider` wrapping `openai.AsyncOpenAI().chat.completions.create()`
- [x] 4.4 Create `core/workflow/providers/factory.py` — `LLMProviderFactory.create()` returning correct provider based on `LLM_PROVIDER` config
- [x] 4.5 Create `core/workflow/providers/__init__.py` — public exports

## 5. Workflow Database Entities (PostgreSQL)

- [x] 5.1 Create `models/workflow/entity/workflow_entity.py` — SQLAlchemy entity for `workflow` table (id, name, description, is_active, audit fields)
- [x] 5.2 Create `models/workflow/entity/workflow_step_entity.py` — SQLAlchemy entity for `workflow_step` table (id, workflow_id FK, name, description, step_order, step_type, llm_prompt, llm_model, llm_max_tokens, on_success_step_id FK, on_failure_step_id FK, is_terminal, config JSONB, audit fields)
- [x] 5.3 Create `models/workflow/entity/workflow_execution_entity.py` — SQLAlchemy entity for `workflow_execution` table (id, workflow_id FK, status, input_data JSONB, output_data JSONB, started_at, finished_at)
- [x] 5.4 Create `models/workflow/entity/step_execution_entity.py` — SQLAlchemy entity for `step_execution` table (id, workflow_execution_id FK, step_id FK, status, input_data JSONB, output_data JSONB, llm_response TEXT, error_message TEXT, started_at, finished_at)
- [x] 5.5 Create domain models: `workflow_model.py`, `workflow_step_model.py`, `workflow_execution_model.py`, `step_execution_model.py` — plain dataclasses
- [x] 5.6 Create mappers: `workflow_mapper.py`, `workflow_step_mapper.py`, `workflow_execution_mapper.py`, `step_execution_mapper.py` — entity ↔ domain
- [x] 5.7 Create `models/workflow/workflow_schemas.py` — Pydantic schemas (CreateSchema, UpdateSchema, ResponseSchema) for all 4 entities
- [x] 5.8 Create `models/workflow/repository/workflow_step_repository.py` — repository with `get_by_workflow_id` ordered by `step_order`
- [x] 5.9 Create `models/workflow/repository/workflow_execution_repository.py` — repository with `create_execution`, `update_execution` methods
- [x] 5.10 Create `models/workflow/repository/step_execution_repository.py` — repository with `save_step_execution` method
- [x] 5.11 Register workflow entities in `core/database.py` `_import_all_models()` for auto table creation

## 6. WorkflowDB Interface & PostgreSQL Implementation

- [x] 6.1 Create `core/workflow/db_interface.py`
- [x] 6.2 Create `core/workflow/postgresql_workflow_db.py`
- [x] 6.3 Create `core/workflow/dynamodb_workflow_db.py`

## 7. Services: Twilio & CinetPay

- [x] 7.1 Create `services/twilio/twilio_service.py`
- [x] 7.2 Create `services/twilio/__init__.py`
- [x] 7.3 Create `services/cinetpay/cinetpay_service.py`
- [x] 7.4 Create `services/cinetpay/__init__.py`

## 8. FastAPI Endpoints

- [x] 8.1 Create `controllers/api/workflow/controller/workflow_controller.py`
- [x] 8.2 Create `controllers/api/twilio/controller/twilio_controller.py`
- [x] 8.3 Create `controllers/api/cinetpay/controller/cinetpay_controller.py`

## 9. Webhook-Triggered Workflow Integration

- [x] 9.1 In `TwilioController`: trigger onboarding workflow via `WorkflowEngine.run()`
- [x] 9.2 In `CinetPayController`: trigger post-payment workflow via `WorkflowEngine.run()`
- [x] 9.3 Implement `HttpHandler` support in `WorkflowEngine._execute_step()` dispatch

## 10. DynamoDB Adapter

- [x] 10.1 Create `core/repository/backends/dynamodb.py`
- [x] 10.2 Create DynamoDB table schema and initialization script
- [x] 10.3 Implement `DynamoDBBackend` in `core/database.py`
- [x] 10.4 Complete `core/workflow/dynamodb_workflow_db.py`

## 11. Tests

- [x] 11.1 Create `tests/unit/workflow/test_engine.py`
- [x] 11.2 Create `tests/unit/workflow/test_llm_handler.py`
- [x] 11.3 Create `tests/unit/workflow/test_function_handler.py`
- [x] 11.4 Create `tests/unit/workflow/test_condition_handler.py`
- [x] 11.5 Create `tests/unit/workflow/test_http_handler.py`
- [x] 11.6 Create `tests/unit/workflow/test_checks.py`
- [x] 11.7 Create `tests/unit/workflow/test_providers.py`
- [x] 11.8 Create `tests/unit/repository/test_sqlalchemy_repository.py`
- [x] 11.9 Create `tests/unit/repository/test_dynamodb_repository.py`
- [x] 11.10 Create `tests/unit/services/test_twilio.py`
- [x] 11.11 Create `tests/unit/services/test_cinetpay.py`
- [x] 11.12 Create `tests/integration/test_workflow_end_to_end.py`
- [x] 11.13 Create `tests/integration/test_webhook_workflow.py`
- [x] 11.14 Add `conftest.py` with fixtures
- [x] 11.15 Add `pyproject.toml` test configuration
