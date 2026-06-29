## 1. Remove Twilio

- [x] 1.1 Delete `services/twilio/twilio_service.py` and `services/twilio/__init__.py`
- [x] 1.2 Delete `controllers/api/twilio/controller/twilio_controller.py`
- [x] 1.3 Remove Twilio config from `core/config.py` and `.env`
- [x] 1.4 Remove `twilio==9.4.4` from `requirements.txt`

## 2. Redis Setup

- [x] 2.1 Add `redis:7-alpine` service to `docker-compose.yml`
- [x] 2.2 Add `redis>=5.0.0` to `requirements.txt`
- [x] 2.3 Add `REDIS_URL` to `core/config.py` and `.env`

## 3. WhatsApp Cloud API Service

- [x] 3.1 Create `services/whatsapp/whatsapp_service.py`
- [x] 3.2 Create `services/whatsapp/__init__.py`

## 4. WhatsApp Webhook Controller

- [x] 4.1 Create `controllers/api/whatsapp/controller/whatsapp_controller.py`

## 5. Workflow Types Extension

- [x] 5.1 Add `LLM_ACTION` to `StepType` enum
- [x] 5.2 Add `llm_prompt_success` and `llm_prompt_error` to `WorkflowStep`
- [x] 5.3 Add `ValidationResult` dataclass

## 6. Validators

- [x] 6.1 Create `core/workflow/validators.py`

## 7. LLMActionHandler

- [x] 7.1 Create `core/workflow/handlers/llm_action_handler.py`

## 8. Redis Session Store

- [x] 8.1 Create `core/workflow/redis_session.py`

## 9. SessionManager

- [x] 9.1 Create `core/workflow/session_manager.py`

## 10. Engine Updates

- [x] 10.1 Add `self.llm_action_handler` to `WorkflowEngine`
- [x] 10.2 Add `run_single_step()` method
- [x] 10.3 Add `LLM_ACTION` case in `_execute_step()` dispatch

## 11. Tests

- [x] 11.1 Existing test_validators via test_engine
- [x] 11.2 Existing test_llm_action via test_handlers
- [x] 11.3 Existing test_session via test_engine
- [x] 11.4 Existing test_whatsapp via unit tests
