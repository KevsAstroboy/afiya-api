## Context

The telemedicine platform (`/home/abdia/telemedecine-api/app`) is a FastAPI application with 25 SQLAlchemy entities on PostgreSQL, following a layered architecture: Controller → Service → Repository → Mapper → Entity/Model. Integration code for WhatsApp (Twilio), payment gateway (CinetPay), and workflow orchestration is entirely absent despite the libraries and schema fields being present. The codebase is tightly coupled to SQLAlchemy async sessions — switching to DynamoDB or any other backend would require rewriting every repository.

## Goals / Non-Goals

**Goals:**
- Introduce a generic `RepositoryInterface[T]` protocol decoupling business logic from the database backend
- Implement a `DatabaseBackend` factory supporting PostgreSQL (SQLAlchemy) and DynamoDB (boto3) with config-driven selection
- Build a dynamic workflow engine driven entirely by DB-parameterized steps, supporting LLM, function, condition, HTTP, and WhatsApp step types
- Ship with PostgreSQL adapter as default, DynamoDB adapter as alternative backend
- Integrate Twilio for WhatsApp send/receive with webhook handling
- Integrate CinetPay for payment initiation and IPN callback processing
- Abstract LLM providers (Anthropic + OpenAI) behind a common interface
- Trigger workflows procedurally from webhook handlers (WhatsApp inbound, CinetPay IPN)
- Follow existing architecture conventions: entity/model/mapper/repository/service/controller layers, Pydantic schemas, FastAPI Depends() injection, soft-delete pattern, auto-router discovery

**Non-Goals:**
- Event bus / pub-sub for workflow triggers (direct procedural call for now)
- Full migration of existing 25 entities to DynamoDB in this change (adapters created, migration done incrementally)
- Authentication middleware (future change)
- Real-time WebSocket/SSE push notifications (future change)
- Migration of existing data from PostgreSQL to DynamoDB (future change)

## Decisions

### D1: RepositoryInterface[T] as the abstraction boundary

**Choice:** Single generic `RepositoryInterface[T]` ABC with `create`, `get_by_id`, `get_all`, `update`, `delete`, `find_one`, `find_by` methods, parameterized by the domain model type `T`.

**Alternatives considered:**
- *Per-entity ABCs (25 interfaces)*: Too much boilerplate, harder to maintain. Rejected.
- *Protocol-based duck typing*: Less explicit contract, harder to validate implementations. Rejected.
- *No abstraction, just config-based import switching*: Would work for swapping but provides no compile-time guarantees. Rejected.

**Rationale:** The generic interface covers 95% of CRUD operations across all entities. Entity-specific methods (e.g., `find_by_transaction_id`) extend via subclassing or are exposed as standalone service methods using `find_one`. One interface, many implementations. The PostgreSQL adapter implements it through a generic `SqlAlchemyRepository[T]` that introspects the SQLAlchemy entity class dynamically — no need to write 25 separate adapter classes.

### D2: PostgreSQL adapter via generic SqlAlchemyRepository

**Choice:** A single `SqlAlchemyRepository[T]` class that uses the SQLAlchemy entity's `__tablename__`, columns, and `Base` metadata to perform CRUD operations generically, without per-entity boilerplate.

```python
class SqlAlchemyRepository(RepositoryInterface[T]):
    def __init__(self, session: AsyncSession, entity_class: type, domain_class: type, mapper: type):
        self.session = session
        self.entity_class = entity_class
        self.domain_class = domain_class
        self.mapper = mapper

    async def get_by_id(self, record_id: Any) -> Optional[T]:
        stmt = select(self.entity_class).where(
            self.entity_class.id == record_id,
            getattr(self.entity_class, 'is_deleted', True) == False
        )
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        return self.mapper.to_domain(entity) if entity else None
```

**Rationale:** The existing 25 repositories already follow an identical pattern. A generic adapter eliminates duplication and is the first step toward the DynamoDB counterpart. Entity-specific repositories can subclass `SqlAlchemyRepository` for custom queries (e.g., `find_by_transaction_id`) without losing the generic CRUD.

### D3: DatabaseBackend factory with FastAPI Depends()

**Choice:** A `DatabaseBackend` abstract class with `get_repository(entity_name)` returning the appropriate `RepositoryInterface` implementation. The backend is selected at startup via `DB_BACKEND` config. FastAPI controllers inject the backend via a `Depends(get_db_backend)` dependency.

```python
# core/config.py addition
DB_BACKEND: str = "postgresql"  # "postgresql" | "dynamodb"

# core/database.py — new dependency
async def get_db_backend(session: AsyncSession = Depends(get_async_session)):
    if settings.DB_BACKEND == "dynamodb":
        yield DynamoDBBackend()
    else:
        yield PostgreSQLBackend(session)
```

**Rationale:** The `Depends()` pattern is already used across all 25 controllers. Replacing `session: AsyncSession = Depends(get_async_session)` with `backend: DatabaseBackend = Depends(get_db_backend)` is a surgical change. For PostgreSQL, the session lifecycle (open/close) is preserved via the async generator. For DynamoDB, no session is needed — the backend handles boto3 connection pooling internally.

### D4: Workflow engine keeps its own DB interface

**Choice:** The `WorkflowEngine` uses a dedicated `WorkflowDBInterface` (not `RepositoryInterface`) for workflow-specific operations: `get_steps_by_workflow`, `create_execution`, `save_step_execution`, `update_execution`, and `find_one` (for business checks). This interface is implemented by both PostgreSQL and DynamoDB adapters.

**Rationale:** The workflow engine's `db` interface is already well-designed in the provided spec and differs from standard CRUD (e.g., `get_steps_by_workflow` joins `workflow_step` with `workflow`). Keeping it separate avoids overloading the generic repository. Business checks (`check_record_exists`, etc.) use `db.find_one()`, which is a natural fit for both SQL and DynamoDB query patterns.

### D5: Direct procedural workflow trigger (not event-driven)

**Choice:** Webhook handlers call `WorkflowEngine.run()` directly after processing the inbound event, rather than emitting events to a message bus.

**Rationale:** For a system of this scale, an event bus (Redis Pub/Sub, Kafka) adds infrastructure complexity without commensurate benefit. The procedural approach is simpler to implement, debug, and test. If future scale demands decoupling, introducing an event bus is a non-breaking change — the engine's `run()` method becomes the event handler.

### D6: LLM Provider abstraction

**Choice:** An `LLMProvider` ABC with `generate(prompt, model, max_tokens) -> str` method, implemented by `AnthropicProvider` and `OpenAIProvider`. Selected via `LLM_PROVIDER` config.

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str, max_tokens: int) -> str: ...

class AnthropicProvider(LLMProvider):
    def __init__(self, client: anthropic.Anthropic): ...

class OpenAIProvider(LLMProvider):
    def __init__(self, client: openai.AsyncOpenAI): ...
```

**Rationale:** The workflow engine's `LLMHandler` only needs `generate()` — it doesn't need provider-specific message formats or streaming. This keeps the abstraction thin and the implementations simple. Adding a new provider (e.g., Google Gemini, Mistral) means adding one class.

### D7: HttpHandler as reusable step type + WhatsApp convenience

**Choice:** A generic `HttpHandler` step type that makes HTTP requests based on `config` (URL, method, headers, body template with context substitution). WhatsApp sending is configured as an HTTP call to Twilio's API via this handler. No separate `WhatsAppHandler` step type.

**Rationale:** Twilio's WhatsApp API is an HTTP REST API. A generic HTTP handler covers it plus any future external API. The Twilio specifics (auth, phone number formatting) live in a `TwilioService` that the HTTP handler can call, or are pre-configured in the step's `config` JSONB. Adding a convenience WhatsApp step type later is straightforward if needed — but starting generic keeps the engine surface small.

```json
// Example step config for WhatsApp via HttpHandler
{
  "step_type": "http",
  "config": {
    "url": "https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
    "method": "POST",
    "auth_type": "basic",
    "auth_username": "{twilio_account_sid}",
    "auth_password": "{twilio_auth_token}",
    "body_template": "To=whatsapp:{input_telephone}&From=whatsapp:{twilio_phone}&Body={step_generation_message_output}",
    "success_status": 201
  }
}
```

### D8: DynamoDB single-table design for workflow tables

**Choice:** All 4 workflow tables (`workflow`, `workflow_step`, `workflow_execution`, `step_execution`) are stored in a single DynamoDB table using the PK/SK + GSI pattern.

```
PK                          SK                          Type              GSI1PK                 GSI1SK
WORKFLOW#<id>               METADATA#<id>               workflow
WORKFLOW#<wf_id>            STEP#<order>                workflow_step     WORKFLOW#<wf_id>
EXECUTION#<id>              METADATA#<id>               workflow_exec     WORKFLOW#<wf_id>       STARTED#<timestamp>
EXECUTION#<exec_id>         STEP_EXEC#<step_id>         step_execution
```

**Rationale:** Single-table design is the DynamoDB best practice. Queries like "get all steps for workflow X by order" become a single PK query on `WORKFLOW#<X>` with `begins_with(SK, 'STEP#')`. The GSI1 enables "get all executions for workflow X sorted by start time".

### D9: File structure follows existing conventions

**Choice:** New modules follow the existing pattern: `entity/`, `model/`, `mapper/`, `repository/`, `schemas`, `service/`, `controller/`. Workflow entities use `BigInteger` IDs for PostgreSQL, with UUID-based alternatives for DynamoDB.

**Rationale:** Consistency with the existing 25-entity codebase reduces cognitive overhead for developers. The auto-router discovery (`discover_and_include_routers`) will automatically pick up new controllers placed in `controllers/api/{name}/controller/{name}_controller.py`.

## Risks / Trade-offs

- **DynamoDB vendor lock-in**: Switching to DynamoDB means AWS lock-in. Mitigation: the `RepositoryInterface` abstraction means any future backend (MongoDB, CockroachDB) can be added as a new adapter class without changing business logic.
- **Generic `SqlAlchemyRepository` may miss edge cases**: Some existing repos have custom queries (e.g., `find_by_transaction_id`). Mitigation: entity-specific repos subclass `SqlAlchemyRepository` and add custom methods. The generic base covers 90% of patterns.
- **DynamoDB costs at scale**: DynamoDB on-demand pricing vs provisioned capacity. Mitigation: start with on-demand for dev, configure provisioned capacity with auto-scaling for production.
- **LLM provider latency**: Workflow steps that call LLMs may take several seconds. Mitigation: workflow execution is async (FastAPI background task or explicit async call). Timeouts configurable per step via `config["timeout_seconds"]`.
- **Twilio / CinetPay external dependency**: If Twilio or CinetPay are down, workflows fail. Mitigation: step-level retry via `config["max_retries"]`. Failed step executions are logged and can be retried manually via the API.
- **No transactional guarantees across workflow steps**: Each step is a separate database transaction. If step 3 fails after step 2 succeeded, step 2's side effects persist. Mitigation: steps should be idempotent where possible; workflow status captures the failure; manual intervention supported via `POST /api/workflow/execute`.
