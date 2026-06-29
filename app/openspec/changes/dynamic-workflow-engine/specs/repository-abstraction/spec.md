## ADDED Requirements

### Requirement: Generic repository interface for all entities
The system SHALL define a `RepositoryInterface[T]` abstract class parameterized by domain model type `T`, providing methods `create`, `get_by_id`, `get_all`, `update`, `delete`, `find_one`, and `find_by`. Every repository implementation MUST implement this interface.

#### Scenario: Create entity via interface
- **WHEN** `repository.create(domain)` is called with a valid domain object
- **THEN** the entity SHALL be persisted and the returned domain object SHALL include the generated ID

#### Scenario: Get entity by ID
- **WHEN** `repository.get_by_id(existing_id)` is called
- **THEN** the domain object SHALL be returned

#### Scenario: Get entity by ID not found
- **WHEN** `repository.get_by_id(nonexistent_id)` is called
- **THEN** `None` SHALL be returned without raising an exception

#### Scenario: Find one by criteria
- **WHEN** `repository.find_one({"transaction_id": "TXN-001"})` is called
- **THEN** the matching domain object SHALL be returned, or `None` if no match

#### Scenario: Soft delete via interface
- **WHEN** `repository.delete(id)` is called on an entity with soft-delete support
- **THEN** `is_deleted` SHALL be set to `TRUE` and `deleted_at` SHALL be set to the current timestamp

### Requirement: Database backend factory with config-driven selection
The system SHALL provide a `DatabaseBackend` abstract class and a factory mechanism that instantiates the correct backend based on the `DB_BACKEND` configuration value (`postgresql` or `dynamodb`).

#### Scenario: PostgreSQL backend selected
- **WHEN** `DB_BACKEND=postgresql` is set
- **THEN** `get_db_backend()` SHALL yield a `PostgreSQLBackend` wrapping an async SQLAlchemy session

#### Scenario: DynamoDB backend selected
- **WHEN** `DB_BACKEND=dynamodb` is set
- **THEN** `get_db_backend()` SHALL yield a `DynamoDBBackend` using boto3

#### Scenario: Invalid backend configuration
- **WHEN** `DB_BACKEND=unknown` is set
- **THEN** the application SHALL raise a clear configuration error at startup

### Requirement: Generic SQLAlchemy repository adapter
The system SHALL provide a `SqlAlchemyRepository[T]` class that implements `RepositoryInterface[T]` for any SQLAlchemy entity class, using the entity's metadata (table name, columns, soft-delete flag) to perform generic CRUD operations without per-entity boilerplate.

#### Scenario: Generic CRUD without entity-specific code
- **WHEN** a `SqlAlchemyRepository` is instantiated with a `UserEntity` class and `User` domain model
- **THEN** `create`, `get_by_id`, `get_all`, `update`, and `delete` SHALL work without writing any entity-specific query

#### Scenario: Automatic soft-delete filtering
- **WHEN** an entity class has an `is_deleted` column
- **THEN** all `get_by_id`, `find_one`, `find_by`, and `get_all` queries SHALL automatically filter `is_deleted == False`

#### Scenario: Entity-specific queries via subclassing
- **WHEN** a `PaiementRepository` subclasses `SqlAlchemyRepository[Paiement]` and adds a `find_by_transaction_id` method
- **THEN** the custom method SHALL coexist with inherited generic CRUD methods

### Requirement: FastAPI dependency injection for database backend
All FastAPI controllers SHALL obtain their database backend via `Depends(get_db_backend)` instead of directly injecting `AsyncSession`. The `get_db_backend` dependency SHALL handle the lifecycle of the underlying connection.

#### Scenario: Controller uses backend dependency
- **WHEN** a controller endpoint declares `backend: DatabaseBackend = Depends(get_db_backend)`
- **THEN** the backend SHALL be injected with the correct implementation for the configured `DB_BACKEND`

#### Scenario: PostgreSQL session lifecycle preserved
- **WHEN** the PostgreSQL backend is active
- **THEN** the async SQLAlchemy session SHALL be properly opened before the request and closed after the response

### Requirement: DynamoDB repository adapter
The system SHALL provide a `DynamoDBRepository[T]` class that implements `RepositoryInterface[T]` using DynamoDB single-table design with boto3. It SHALL support PK/SK patterns and GSI-based queries.

#### Scenario: DynamoDB create entity
- **WHEN** `dynamo_repo.create(domain)` is called
- **THEN** the item SHALL be stored in DynamoDB with appropriate PK and SK attributes derived from the entity type

#### Scenario: DynamoDB query by GSI
- **WHEN** `dynamo_repo.find_by({"gsi_field": "value"})` is called
- **THEN** the GSI SHALL be queried and matching items SHALL be returned as domain objects

### Requirement: Workflow-specific database interface
The workflow engine SHALL use a dedicated `WorkflowDBInterface` for its storage needs, separate from the generic `RepositoryInterface`. This interface SHALL provide `get_steps_by_workflow`, `create_execution`, `save_step_execution`, `update_execution`, and `find_one` methods.

#### Scenario: Workflow steps are returned in order
- **WHEN** `get_steps_by_workflow(wf_id)` is called
- **THEN** steps SHALL be returned sorted by `step_order` ascending

#### Scenario: Execution trace is saved atomically
- **WHEN** `save_step_execution(execution_id, result)` is called
- **THEN** a row SHALL be inserted with the step ID, execution ID, status, output, error, and timestamps

#### Scenario: WorkflowDB find_one delegates to appropriate repository
- **WHEN** `find_one("clients", {"telephone": "0700000000"})` is called
- **THEN** the implementation SHALL delegate to the `clients` entity's repository `find_one` method

### Requirement: Backend-agnostic service layer
Business service classes SHALL depend on `RepositoryInterface` abstractions, not concrete implementations. They SHALL NOT import SQLAlchemy `AsyncSession` directly.

#### Scenario: Service works with any backend
- **WHEN** a service method is called with a PostgreSQL backend and then with a DynamoDB backend
- **THEN** the service SHALL behave identically for both backends
