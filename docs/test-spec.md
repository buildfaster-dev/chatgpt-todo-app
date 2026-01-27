# Test Specification Document

## ChatGPT ToDo App with AI Task Decomposition

| **Document Version** | 1.0 |
|---|---|
| **Last Updated** | January 2026 |
| **Status** | Draft |
| **Related PRD** | PRD v1.0 |
| **Related TDD** | TDD v1.0 |

---

## 1. Test Strategy Overview

### 1.1 Testing Approach

This test specification follows a **pyramid testing strategy** optimized for a learning project:

```
        ┌─────────────┐
        │    E2E      │  ← Few, high-value MCP flow tests
        │   Tests     │
        ├─────────────┤
        │ Integration │  ← Tool handlers + real SQLite
        │   Tests     │
        ├─────────────┤
        │    Unit     │  ← Many, fast, isolated tests
        │   Tests     │
        └─────────────┘
```

### 1.2 Test Types and Priorities

| Priority | Test Type | Scope | Target Coverage | Rationale |
|----------|-----------|-------|-----------------|-----------|
| **P0** | Unit Tests | Individual functions, models, schemas | 80% line coverage | Fast feedback, catch bugs early |
| **P1** | Integration Tests | Tool handlers + database | All CRUD paths | Verify component interaction |
| **P2** | E2E Tests | Full MCP request/response cycle | Critical user flows | Validate protocol compliance |
| **P3** | UI Snapshot Tests | HTML component output | All card types | Prevent UI regressions |

### 1.3 Coverage Targets

| Module | Target Coverage | Critical Paths |
|--------|-----------------|----------------|
| `src/tools/task_tools.py` | 90% | All tool handlers |
| `src/tools/schemas.py` | 85% | Validation logic |
| `src/database/models.py` | 90% | All CRUD operations |
| `src/database/connection.py` | 80% | Connection management |
| `src/ui/components.py` | 75% | Card rendering |
| `src/server.py` | 70% | Request routing |

### 1.4 Tools and Frameworks

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | 8.x | Test framework |
| pytest-asyncio | 0.23+ | Async test support |
| pytest-cov | 4.x | Coverage reporting |
| aiosqlite | 0.19+ | Async SQLite for tests |
| pytest-snapshot | Latest | UI snapshot testing |
| httpx | 0.27+ | Async HTTP client for E2E tests |
| factory-boy | 3.x | Test data factories |

### 1.5 Test Execution Strategy

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest -m "not slow"         # Skip slow tests

# Run tests for specific module
pytest tests/unit/test_task_tools.py -v
```

---

## 2. Unit Tests Specification

### 2.1 Pydantic Models (`src/tools/schemas.py`)

#### 2.1.1 TaskCreate Model

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-SCH-001 | Valid task creation with title only | `{"title": "Buy groceries"}` | Valid TaskCreate instance | None |
| UT-SCH-002 | Valid task creation with parent_id | `{"title": "Buy milk", "parent_id": 1}` | Valid TaskCreate with parent_id=1 | None |
| UT-SCH-003 | Reject empty title | `{"title": ""}` | ValidationError: min_length=1 | None |
| UT-SCH-004 | Reject whitespace-only title | `{"title": "   "}` | ValidationError after strip() | None |
| UT-SCH-005 | Reject title exceeding max length | `{"title": "a" * 501}` | ValidationError: max_length=500 | None |
| UT-SCH-006 | Reject negative parent_id | `{"title": "Task", "parent_id": -1}` | ValidationError: ge=1 | None |
| UT-SCH-007 | Reject zero parent_id | `{"title": "Task", "parent_id": 0}` | ValidationError: ge=1 | None |
| UT-SCH-008 | Strip whitespace from title | `{"title": "  Buy groceries  "}` | title = "Buy groceries" | None |
| UT-SCH-009 | Accept None parent_id | `{"title": "Task", "parent_id": None}` | Valid with parent_id=None | None |
| UT-SCH-010 | Missing required title field | `{}` | ValidationError: field required | None |

#### 2.1.2 Task Model

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-SCH-011 | Create Task from database row | DB row dict with all fields | Valid Task instance | None |
| UT-SCH-012 | Default completed is False | Task without completed field | completed = False | None |
| UT-SCH-013 | Default subtasks is empty list | Task without subtasks | subtasks = [] | None |
| UT-SCH-014 | JSON serialization includes all fields | Valid Task instance | JSON with id, title, completed, created_at, parent_id, subtasks | None |
| UT-SCH-015 | Nested subtasks serialize correctly | Task with 3 subtasks | JSON includes subtasks array | None |

#### 2.1.3 Tool Input Schemas

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-SCH-020 | ListTasksInput default filter | `{}` | filter = "all" | None |
| UT-SCH-021 | ListTasksInput valid filter values | `{"filter": "complete"}` | Valid with filter="complete" | None |
| UT-SCH-022 | ListTasksInput invalid filter | `{"filter": "invalid"}` | ValidationError: not in enum | None |
| UT-SCH-023 | CompleteTaskInput valid | `{"task_id": 1}` | Valid instance | None |
| UT-SCH-024 | CompleteTaskInput missing task_id | `{}` | ValidationError: required | None |
| UT-SCH-025 | DeleteTaskInput valid | `{"task_id": 5}` | Valid instance | None |
| UT-SCH-026 | DecomposeTaskInput valid | `{"task_id": 1, "subtask_titles": ["a", "b", "c"]}` | Valid instance | None |
| UT-SCH-027 | DecomposeTaskInput too few subtasks | `{"task_id": 1, "subtask_titles": ["a", "b"]}` | ValidationError: minItems=3 | None |
| UT-SCH-028 | DecomposeTaskInput too many subtasks | `{"task_id": 1, "subtask_titles": ["a"]*11}` | ValidationError: maxItems=10 | None |

### 2.2 Database Layer (`src/database/models.py`)

#### 2.2.1 TaskRepository - Create Operations

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-DB-001 | Create task with valid title | `title="Buy groceries"` | Task with auto-generated id, completed=False | In-memory SQLite |
| UT-DB-002 | Create task with parent_id | `title="Buy milk", parent_id=1` | Task with parent_id=1 | In-memory SQLite |
| UT-DB-003 | Create task with non-existent parent | `title="Task", parent_id=999` | ForeignKeyError or graceful handling | In-memory SQLite |
| UT-DB-004 | created_at is auto-populated | `title="Task"` | created_at is close to current time | In-memory SQLite |
| UT-DB-005 | Create multiple tasks sequentially | 3 create calls | IDs are 1, 2, 3 (auto-increment) | In-memory SQLite |

#### 2.2.2 TaskRepository - Read Operations

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-DB-010 | Get all tasks from empty database | `filter="all"` | Empty list | In-memory SQLite |
| UT-DB-011 | Get all tasks | `filter="all"` (3 tasks exist) | List of 3 tasks | In-memory SQLite |
| UT-DB-012 | Filter incomplete tasks | `filter="incomplete"` | Only tasks with completed=False | In-memory SQLite |
| UT-DB-013 | Filter complete tasks | `filter="complete"` | Only tasks with completed=True | In-memory SQLite |
| UT-DB-014 | Get task by ID - exists | `task_id=1` | Task with id=1 | In-memory SQLite |
| UT-DB-015 | Get task by ID - not found | `task_id=999` | None | In-memory SQLite |
| UT-DB-016 | Get subtasks by parent_id | `parent_id=1` | List of child tasks | In-memory SQLite |
| UT-DB-017 | Get tasks with subtasks populated | `filter="all"` | Tasks include subtasks array | In-memory SQLite |

#### 2.2.3 TaskRepository - Update Operations

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-DB-020 | Complete a task | `task_id=1, completed=True` | Task with completed=True | In-memory SQLite |
| UT-DB-021 | Uncomplete a task | `task_id=1, completed=False` | Task with completed=False | In-memory SQLite |
| UT-DB-022 | Complete non-existent task | `task_id=999` | TaskNotFoundError | In-memory SQLite |
| UT-DB-023 | Complete already completed task | Complete task twice | Idempotent - still completed=True | In-memory SQLite |

#### 2.2.4 TaskRepository - Delete Operations

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-DB-030 | Delete existing task | `task_id=1` | True, task removed | In-memory SQLite |
| UT-DB-031 | Delete non-existent task | `task_id=999` | False or TaskNotFoundError | In-memory SQLite |
| UT-DB-032 | Cascade delete subtasks | Delete parent with 3 subtasks | Parent and all subtasks removed | In-memory SQLite |
| UT-DB-033 | Delete subtask independently | Delete subtask, parent exists | Only subtask removed | In-memory SQLite |

#### 2.2.5 TaskRepository - Bulk Operations

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-DB-040 | Create multiple subtasks | `parent_id=1, titles=["a","b","c"]` | 3 subtasks with parent_id=1 | In-memory SQLite |
| UT-DB-041 | Create subtasks for non-existent parent | `parent_id=999, titles=["a"]` | Error or empty result | In-memory SQLite |

### 2.3 UI Components (`src/ui/components.py`)

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-UI-001 | Render single task card - incomplete | Task(completed=False) | HTML with unchecked indicator | None |
| UT-UI-002 | Render single task card - complete | Task(completed=True) | HTML with checked indicator, strikethrough | None |
| UT-UI-003 | Render task list - empty | `[]` | Empty state message HTML | None |
| UT-UI-004 | Render task list - multiple tasks | 3 tasks | HTML list with 3 items | None |
| UT-UI-005 | Render confirmation - task added | `message, Task` | Confirmation HTML with task details | None |
| UT-UI-006 | Render confirmation - task deleted | `message, None` | Confirmation HTML without task | None |
| UT-UI-007 | Render task hierarchy | Parent + 3 subtasks | Nested HTML structure | None |
| UT-UI-008 | Task card includes action buttons | Task | HTML includes complete/delete buttons | None |
| UT-UI-009 | Special characters escaped in title | Task(title="<script>") | HTML-escaped output | None |
| UT-UI-010 | Long title truncated appropriately | Task(title="a"*200) | Title truncated or wrapped | None |

### 2.4 Tool Handlers (`src/tools/task_tools.py`)

#### 2.4.1 add_task Handler

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-TH-001 | Add task returns task and UI | `{"title": "Test"}` | `{task: {...}, ui: "..."}` | Mock TaskRepository |
| UT-TH-002 | Add task calls repository create | `{"title": "Test"}` | `repository.create()` called with title | Mock TaskRepository |
| UT-TH-003 | Add task with parent_id | `{"title": "Sub", "parent_id": 1}` | `repository.create()` called with parent_id | Mock TaskRepository |
| UT-TH-004 | Add task validation error | `{"title": ""}` | ValidationError raised | Mock TaskRepository |

#### 2.4.2 list_tasks Handler

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-TH-010 | List tasks returns array and UI | `{}` | `{tasks: [...], total: n, ui: "..."}` | Mock TaskRepository |
| UT-TH-011 | List tasks with filter | `{"filter": "incomplete"}` | `repository.get_all(filter="incomplete")` | Mock TaskRepository |
| UT-TH-012 | List tasks with parent_id | `{"parent_id": 1}` | `repository.get_all(parent_id=1)` | Mock TaskRepository |
| UT-TH-013 | List tasks empty result | `{}` (no tasks) | `{tasks: [], total: 0, ui: "empty state"}` | Mock TaskRepository |

#### 2.4.3 complete_task Handler

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-TH-020 | Complete task returns updated task | `{"task_id": 1}` | `{task: {completed: true}, ui: "..."}` | Mock TaskRepository |
| UT-TH-021 | Complete task calls repository | `{"task_id": 1}` | `repository.update_completed(1, True)` | Mock TaskRepository |
| UT-TH-022 | Complete non-existent task | `{"task_id": 999}` | Error response with TASK_NOT_FOUND | Mock TaskRepository (raises) |

#### 2.4.4 delete_task Handler

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-TH-030 | Delete task returns confirmation | `{"task_id": 1}` | `{deleted: true, task_id: 1, ui: "..."}` | Mock TaskRepository |
| UT-TH-031 | Delete task calls repository | `{"task_id": 1}` | `repository.delete(1)` called | Mock TaskRepository |
| UT-TH-032 | Delete non-existent task | `{"task_id": 999}` | Error response with TASK_NOT_FOUND | Mock TaskRepository |
| UT-TH-033 | Delete returns subtasks count | Parent with 3 subtasks | `{subtasks_deleted: 3}` | Mock TaskRepository |

#### 2.4.5 decompose_task Handler

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-TH-040 | Decompose creates subtasks | `{"task_id": 1, "subtask_titles": ["a","b","c"]}` | `{parent_task, subtasks: [...], ui}` | Mock TaskRepository |
| UT-TH-041 | Decompose verifies parent exists | `{"task_id": 1, ...}` | `repository.get_by_id(1)` called first | Mock TaskRepository |
| UT-TH-042 | Decompose non-existent parent | `{"task_id": 999, ...}` | Error TASK_NOT_FOUND | Mock TaskRepository |
| UT-TH-043 | Decompose calls bulk create | `{..., "subtask_titles": ["a","b","c"]}` | `repository.create_subtasks()` called | Mock TaskRepository |

### 2.5 Error Handling

| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|
| UT-ERR-001 | ToolError serializes correctly | `ToolError(code=..., message=...)` | Valid JSON structure | None |
| UT-ERR-002 | ValidationError mapped to VALIDATION_ERROR | Pydantic ValidationError | `{error: {code: "VALIDATION_ERROR"}}` | None |
| UT-ERR-003 | TaskNotFoundError mapped correctly | Custom TaskNotFoundError | `{error: {code: "TASK_NOT_FOUND"}}` | None |
| UT-ERR-004 | Database error handled gracefully | SQLite exception | `{error: {code: "DATABASE_ERROR"}}` | Mock DB raises |
| UT-ERR-005 | Unexpected error logged and handled | Random exception | `{error: {code: "INTERNAL_ERROR"}}` | Mock raises |

---

## 3. Integration Tests Specification

### 3.1 Tool + Database Integration

#### 3.1.1 add_task Integration

| ID | Description | Setup | Steps | Assertions |
|----|-------------|-------|-------|------------|
| IT-ADD-001 | Add task persists to database | Empty DB | Call `add_task({"title": "Test"})` | Task exists in DB with correct title |
| IT-ADD-002 | Add subtask links to parent | 1 parent task | Call `add_task({"title": "Sub", "parent_id": 1})` | Subtask has parent_id=1 in DB |
| IT-ADD-003 | Add task returns valid UI | Empty DB | Call `add_task({"title": "Test"})` | Response `ui` is valid HTML |
| IT-ADD-004 | Add multiple tasks sequentially | Empty DB | Add 5 tasks | All 5 tasks in DB, IDs sequential |

#### 3.1.2 list_tasks Integration

| ID | Description | Setup | Steps | Assertions |
|----|-------------|-------|-------|------------|
| IT-LIST-001 | List returns all tasks | 3 tasks in DB | Call `list_tasks({})` | 3 tasks returned |
| IT-LIST-002 | List respects filter | 2 complete, 2 incomplete | Call `list_tasks({"filter": "incomplete"})` | 2 tasks returned |
| IT-LIST-003 | List includes subtasks | Parent + 2 subtasks | Call `list_tasks({})` | Parent has `subtasks` array |
| IT-LIST-004 | List empty database | Empty DB | Call `list_tasks({})` | `{tasks: [], total: 0}` |
| IT-LIST-005 | List by parent_id | Parent + 3 subtasks | Call `list_tasks({"parent_id": 1})` | 3 subtasks returned |

#### 3.1.3 complete_task Integration

| ID | Description | Setup | Steps | Assertions |
|----|-------------|-------|-------|------------|
| IT-COMP-001 | Complete updates database | 1 incomplete task | Call `complete_task({"task_id": 1})` | Task in DB has completed=True |
| IT-COMP-002 | Complete is idempotent | 1 complete task | Call `complete_task({"task_id": 1})` twice | No error, still completed |
| IT-COMP-003 | Complete returns updated task | 1 incomplete task | Call `complete_task({"task_id": 1})` | Response task has completed=True |
| IT-COMP-004 | Complete non-existent fails | Empty DB | Call `complete_task({"task_id": 1})` | Error response returned |

#### 3.1.4 delete_task Integration

| ID | Description | Setup | Steps | Assertions |
|----|-------------|-------|-------|------------|
| IT-DEL-001 | Delete removes from database | 1 task | Call `delete_task({"task_id": 1})` | Task not in DB |
| IT-DEL-002 | Delete cascades to subtasks | Parent + 2 subtasks | Call `delete_task({"task_id": 1})` | All 3 tasks removed |
| IT-DEL-003 | Delete subtask only | Parent + 2 subtasks | Call `delete_task({"task_id": 2})` | Only subtask removed, parent exists |
| IT-DEL-004 | Delete returns count | Parent + 3 subtasks | Call `delete_task({"task_id": 1})` | Response `subtasks_deleted: 3` |

#### 3.1.5 decompose_task Integration

| ID | Description | Setup | Steps | Assertions |
|----|-------------|-------|-------|------------|
| IT-DEC-001 | Decompose creates subtasks in DB | 1 parent task | Call `decompose_task({"task_id": 1, "subtask_titles": ["a","b","c"]})` | 3 subtasks in DB with parent_id=1 |
| IT-DEC-002 | Decompose returns hierarchy | 1 parent task | Call decompose | Response includes parent and subtasks |
| IT-DEC-003 | Decompose preserves parent unchanged | 1 task, completed=False | Call decompose | Parent still has original values |

### 3.2 Database Connection Integration

| ID | Description | Setup | Steps | Assertions |
|----|-------------|-------|-------|------------|
| IT-CONN-001 | Database created on first run | No DB file | Start server | DB file exists at configured path |
| IT-CONN-002 | Schema initialized correctly | New DB | Query schema | All tables and indexes exist |
| IT-CONN-003 | Connection handles concurrent requests | Running server | 10 concurrent add_task calls | All succeed, no corruption |
| IT-CONN-004 | Connection recovers from error | Force connection error | Next request | Subsequent requests succeed |

### 3.3 Error Handling Integration

| ID | Description | Setup | Steps | Assertions |
|----|-------------|-------|-------|------------|
| IT-ERR-001 | Invalid input returns structured error | Running server | Call `add_task({"title": ""})` | Response has `error.code`, `error.message` |
| IT-ERR-002 | Not found returns 404 equivalent | 0 tasks | Call `complete_task({"task_id": 999})` | `error.code == "TASK_NOT_FOUND"` |
| IT-ERR-003 | Database error returns 500 equivalent | Corrupt DB | Any operation | `error.code == "DATABASE_ERROR"` |

---

## 4. Test Data Requirements

### 4.1 Fixtures

#### 4.1.1 Database Fixtures

```python
# tests/conftest.py

@pytest.fixture
async def empty_db():
    """Fresh in-memory database with schema."""
    async with aiosqlite.connect(":memory:") as db:
        await init_schema(db)
        yield db

@pytest.fixture
async def db_with_tasks(empty_db):
    """Database with sample tasks."""
    repo = TaskRepository(empty_db)
    await repo.create("Buy groceries")
    await repo.create("Call mom")
    await repo.create("Finish report")
    yield empty_db

@pytest.fixture
async def db_with_hierarchy(empty_db):
    """Database with parent and subtasks."""
    repo = TaskRepository(empty_db)
    parent = await repo.create("Plan party")
    await repo.create("Choose venue", parent_id=parent.id)
    await repo.create("Create guest list", parent_id=parent.id)
    await repo.create("Order cake", parent_id=parent.id)
    yield empty_db

@pytest.fixture
async def db_with_mixed_status(empty_db):
    """Database with complete and incomplete tasks."""
    repo = TaskRepository(empty_db)
    t1 = await repo.create("Complete task 1")
    t2 = await repo.create("Complete task 2")
    await repo.create("Incomplete task 1")
    await repo.create("Incomplete task 2")
    await repo.update_completed(t1.id, True)
    await repo.update_completed(t2.id, True)
    yield empty_db
```

#### 4.1.2 Model Fixtures

```python
@pytest.fixture
def sample_task():
    """Sample Task instance."""
    return Task(
        id=1,
        title="Buy groceries",
        completed=False,
        created_at=datetime(2026, 1, 25, 10, 30, 0),
        parent_id=None,
        subtasks=[]
    )

@pytest.fixture
def sample_task_with_subtasks(sample_task):
    """Task with nested subtasks."""
    sample_task.subtasks = [
        Task(id=2, title="Buy milk", completed=False, created_at=datetime.now(), parent_id=1),
        Task(id=3, title="Buy bread", completed=True, created_at=datetime.now(), parent_id=1),
    ]
    return sample_task

@pytest.fixture
def completed_task():
    """Completed task instance."""
    return Task(
        id=1,
        title="Finished task",
        completed=True,
        created_at=datetime(2026, 1, 24, 9, 0, 0),
        parent_id=None
    )
```

### 4.2 Test Data Factories

```python
# tests/factories.py
import factory
from datetime import datetime

class TaskFactory(factory.Factory):
    class Meta:
        model = Task
    
    id = factory.Sequence(lambda n: n + 1)
    title = factory.Faker('sentence', nb_words=4)
    completed = False
    created_at = factory.LazyFunction(datetime.now)
    parent_id = None
    subtasks = factory.List([])

class TaskCreateFactory(factory.Factory):
    class Meta:
        model = TaskCreate
    
    title = factory.Faker('sentence', nb_words=4)
    parent_id = None
```

### 4.3 Sample Test Data

#### Valid Inputs

| Field | Valid Examples |
|-------|----------------|
| `title` | "Buy groceries", "a", "A"*500, "Task with émojis 🎉" |
| `parent_id` | 1, 100, None |
| `filter` | "all", "complete", "incomplete" |
| `task_id` | 1, 100, 999999 |
| `subtask_titles` | ["a","b","c"], ["x"]*10, ["Task 1", "Task 2", "Task 3"] |

#### Invalid Inputs (for negative testing)

| Field | Invalid Examples | Expected Error |
|-------|------------------|----------------|
| `title` | "", "   ", None, "a"*501 | ValidationError |
| `parent_id` | -1, 0, "abc", 1.5 | ValidationError |
| `filter` | "invalid", "ALL", 123 | ValidationError |
| `task_id` | -1, 0, "abc", None | ValidationError |
| `subtask_titles` | ["a"], ["a","b"], ["x"]*11, [] | ValidationError |

---

## 5. Mock Specifications

### 5.1 TaskRepository Mock

```python
# tests/mocks.py
from unittest.mock import AsyncMock, MagicMock

def create_mock_repository():
    """Create a fully mocked TaskRepository."""
    mock = AsyncMock()
    
    # Default successful responses
    mock.create.return_value = Task(
        id=1, title="Test", completed=False, 
        created_at=datetime.now(), parent_id=None
    )
    mock.get_all.return_value = []
    mock.get_by_id.return_value = Task(
        id=1, title="Test", completed=False,
        created_at=datetime.now(), parent_id=None
    )
    mock.update_completed.return_value = Task(
        id=1, title="Test", completed=True,
        created_at=datetime.now(), parent_id=None
    )
    mock.delete.return_value = True
    mock.create_subtasks.return_value = []
    
    return mock

def create_failing_repository():
    """Repository that raises errors."""
    mock = AsyncMock()
    mock.create.side_effect = DatabaseError("Connection failed")
    mock.get_all.side_effect = DatabaseError("Connection failed")
    return mock
```

### 5.2 Mock Responses by Scenario

#### TaskRepository.create()

| Scenario | Mock Configuration | Return/Raise |
|----------|-------------------|--------------|
| Success | Default | Task instance |
| Duplicate (if enforced) | `side_effect=IntegrityError` | IntegrityError |
| DB connection error | `side_effect=DatabaseError` | DatabaseError |
| Invalid parent | `side_effect=ForeignKeyError` | ForeignKeyError |

#### TaskRepository.get_by_id()

| Scenario | Mock Configuration | Return/Raise |
|----------|-------------------|--------------|
| Task found | `return_value=Task(...)` | Task instance |
| Task not found | `return_value=None` | None |
| DB error | `side_effect=DatabaseError` | DatabaseError |

#### TaskRepository.update_completed()

| Scenario | Mock Configuration | Return/Raise |
|----------|-------------------|--------------|
| Success | `return_value=Task(completed=True)` | Updated Task |
| Not found | `side_effect=TaskNotFoundError` | TaskNotFoundError |
| DB error | `side_effect=DatabaseError` | DatabaseError |

#### TaskRepository.delete()

| Scenario | Mock Configuration | Return/Raise |
|----------|-------------------|--------------|
| Success | `return_value=True` | True |
| Not found | `return_value=False` or `side_effect=TaskNotFoundError` | False/Error |
| DB error | `side_effect=DatabaseError` | DatabaseError |

### 5.3 Database Connection Mock

```python
@pytest.fixture
def mock_db_connection():
    """Mock aiosqlite connection."""
    mock = AsyncMock()
    mock.execute = AsyncMock()
    mock.fetchone = AsyncMock(return_value=(1, "Test", False, "2026-01-25", None))
    mock.fetchall = AsyncMock(return_value=[])
    mock.commit = AsyncMock()
    return mock
```

### 5.4 When to Use Mocks vs Real

| Test Type | Use Mock | Use Real |
|-----------|----------|----------|
| Unit tests for tool handlers | ✅ Repository | ❌ |
| Unit tests for schemas | ❌ | ✅ (no external deps) |
| Unit tests for UI components | ❌ | ✅ (no external deps) |
| Integration tests | ❌ | ✅ In-memory SQLite |
| E2E tests | ❌ | ✅ Real server + DB |
| Error scenario tests | ✅ (force errors) | ❌ |

---

## 6. Test Cases per User Story

### 6.1 US-01: Add Task Conversationally

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| User can say "Add task: Buy groceries" | UT-TH-001, IT-ADD-001 |
| Task is created with title extracted | UT-SCH-001, UT-DB-001 |
| Confirmation shown via inline card | UT-UI-005, IT-ADD-003 |
| Task persists in SQLite | IT-ADD-001, IT-ADD-004 |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US01-TC01 | Add task with simple title | Integration |
| US01-TC02 | Add task with special characters | Integration |
| US01-TC03 | Add task with maximum length title | Integration |
| US01-TC04 | Add task with empty title fails | Unit |
| US01-TC05 | Confirmation card displays correct title | Unit |

### 6.2 US-02: View All Tasks

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| User can say "Show my tasks" | IT-LIST-001 |
| Tasks displayed in inline card/carousel | UT-UI-004, IT-LIST-001 |
| Shows task title and completion status | UT-UI-001, UT-UI-002 |
| Empty state handled gracefully | UT-UI-003, IT-LIST-004 |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US02-TC01 | List tasks returns all tasks | Integration |
| US02-TC02 | Empty list shows friendly message | Integration |
| US02-TC03 | Tasks show correct completion indicators | Unit |
| US02-TC04 | Large task list renders without error | Integration |

### 6.3 US-03: Mark Task Complete

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| User can say "Complete task 1" | IT-COMP-001 |
| Task status updates to complete | UT-TH-020, IT-COMP-001 |
| Visual confirmation shown | UT-UI-002 |
| Database updated | IT-COMP-001 |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US03-TC01 | Complete task by ID | Integration |
| US03-TC02 | Complete non-existent task returns error | Integration |
| US03-TC03 | Complete already-complete task is idempotent | Integration |
| US03-TC04 | UI shows checkmark after completion | Unit |

### 6.4 US-04: Delete Task

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| User can say "Delete task 2" | IT-DEL-001 |
| Task removed from database | IT-DEL-001 |
| Confirmation shown | UT-UI-006 |
| Task list updates | IT-DEL-001 |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US04-TC01 | Delete task by ID | Integration |
| US04-TC02 | Delete non-existent task returns error | Integration |
| US04-TC03 | Delete parent cascades to subtasks | Integration |
| US04-TC04 | Confirmation shows deleted task details | Unit |

### 6.5 US-05: MCP Server Tools

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| Tools registered: add_task, list_tasks, etc. | E2E-001 |
| Each tool has JSON Schema | UT-SCH-* |
| Tool metadata includes descriptions | E2E-002 |
| Server responds to list_tools and call_tool | E2E-001, E2E-003 |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US05-TC01 | list_tools returns all 5 tools | E2E |
| US05-TC02 | Tool schemas are valid JSON Schema | Unit |
| US05-TC03 | call_tool routes to correct handler | Integration |
| US05-TC04 | Unknown tool returns error | E2E |

### 6.6 US-06: SQLite Persistence

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| SQLite database created on first run | IT-CONN-001 |
| Schema includes required columns | IT-CONN-002 |
| CRUD operations work correctly | IT-ADD-*, IT-LIST-*, IT-COMP-*, IT-DEL-* |
| Database location configurable | IT-CONN-001 |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US06-TC01 | Database file created if not exists | Integration |
| US06-TC02 | Schema has all required columns and indexes | Integration |
| US06-TC03 | Data persists across repository instances | Integration |
| US06-TC04 | Custom DATABASE_PATH environment variable works | Integration |

### 6.7 US-07: AI Task Decomposition

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| Decompose complex task into subtasks | IT-DEC-001 |
| Generate 3-10 contextual subtasks | UT-SCH-026, UT-SCH-027, UT-SCH-028 |
| Subtasks saved with parent_id | IT-DEC-001 |
| Subtasks displayed hierarchically | UT-UI-007 |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US07-TC01 | Decompose creates linked subtasks | Integration |
| US07-TC02 | Minimum 3 subtasks enforced | Unit |
| US07-TC03 | Maximum 10 subtasks enforced | Unit |
| US07-TC04 | Hierarchy renders correctly in UI | Unit |
| US07-TC05 | Decompose non-existent task fails | Integration |

### 6.8 US-08: Inline Card UI

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| Task list renders as inline card | UT-UI-004 |
| Tasks show title, status, actions | UT-UI-001, UT-UI-002, UT-UI-008 |
| Cards follow Apps SDK guidelines | UT-UI-* (snapshot tests) |
| Responsive on web and mobile | Manual test |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US08-TC01 | Card renders valid HTML | Unit |
| US08-TC02 | Action buttons present | Unit |
| US08-TC03 | Status indicator correct | Unit |
| US08-TC04 | HTML escaped properly | Unit |

### 6.9 US-10: Filter Tasks by Status

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| Filter incomplete tasks | IT-LIST-002 |
| Filter complete tasks | IT-LIST-002 |
| Filter applied to list_tasks | UT-TH-011 |
| Results display filtered subset | IT-LIST-002 |

**Additional Test Cases:**

| ID | Description | Type |
|----|-------------|------|
| US10-TC01 | Filter "incomplete" returns only incomplete | Integration |
| US10-TC02 | Filter "complete" returns only complete | Integration |
| US10-TC03 | Filter "all" returns everything | Integration |
| US10-TC04 | Invalid filter value rejected | Unit |

---

## 7. E2E Tests Specification

### 7.1 MCP Protocol Flow Tests

| ID | Description | Setup | Steps | Assertions |
|----|-------------|-------|-------|------------|
| E2E-001 | list_tools returns all tools | Running server | POST /mcp with list_tools request | Response includes 5 tool definitions |
| E2E-002 | Tool descriptions present | Running server | Parse list_tools response | Each tool has non-empty description |
| E2E-003 | call_tool executes add_task | Running server | POST /mcp with call_tool(add_task) | Task created, response includes task and UI |
| E2E-004 | call_tool handles unknown tool | Running server | POST /mcp with call_tool(unknown_tool) | Error response with appropriate code |
| E2E-005 | Full CRUD flow | Running server | Add → List → Complete → Delete | All operations succeed, state correct |

### 7.2 Full User Flow Tests

| ID | Description | Steps | Assertions |
|----|-------------|-------|------------|
| E2E-FLOW-001 | Add and list task | 1. Add "Buy groceries" 2. List tasks | Task appears in list |
| E2E-FLOW-002 | Complete task flow | 1. Add task 2. Complete it 3. Filter complete | Task in complete filter |
| E2E-FLOW-003 | Delete task flow | 1. Add task 2. Delete it 3. List tasks | Task not in list |
| E2E-FLOW-004 | Subtask flow | 1. Add parent 2. Decompose 3. List | Parent shows with subtasks |
| E2E-FLOW-005 | Cascade delete | 1. Add parent 2. Decompose 3. Delete parent 4. List | All tasks removed |

---

## 8. Test Execution Checklist

### 8.1 Pre-Release Checklist

- [ ] All unit tests pass (`pytest tests/unit/`)
- [ ] All integration tests pass (`pytest tests/integration/`)
- [ ] All E2E tests pass (`pytest tests/e2e/`)
- [ ] Coverage >= 80% for critical modules
- [ ] No failing snapshot tests
- [ ] All P0 user story test cases pass
- [ ] Manual smoke test completed
- [ ] Linting passes (`ruff check src/`)
- [ ] Type checking passes (`mypy src/`)

### 8.2 CI Pipeline Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -e ".[dev]"
      
      - name: Run linting
        run: ruff check src/
      
      - name: Run type checking
        run: mypy src/
      
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 9. Example Test Code

### 9.1 Unit Test Example

```python
# tests/unit/test_task_tools.py
import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from src.tools.task_tools import add_task_handler
from src.tools.schemas import Task

@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.create.return_value = Task(
        id=1,
        title="Test task",
        completed=False,
        created_at=datetime.now(),
        parent_id=None,
        subtasks=[]
    )
    return repo

@pytest.mark.asyncio
async def test_add_task_returns_task_and_ui(mock_repository, monkeypatch):
    """UT-TH-001: Add task returns task and UI."""
    monkeypatch.setattr("src.tools.task_tools.repository", mock_repository)
    
    result = await add_task_handler({"title": "Test task"})
    
    assert "task" in result
    assert result["task"]["title"] == "Test task"
    assert result["task"]["completed"] is False
    assert "ui" in result
    assert isinstance(result["ui"], str)

@pytest.mark.asyncio
async def test_add_task_calls_repository_create(mock_repository, monkeypatch):
    """UT-TH-002: Add task calls repository create."""
    monkeypatch.setattr("src.tools.task_tools.repository", mock_repository)
    
    await add_task_handler({"title": "Test task"})
    
    mock_repository.create.assert_called_once_with("Test task", parent_id=None)
```

### 9.2 Integration Test Example

```python
# tests/integration/test_tools_integration.py
import pytest
import aiosqlite

from src.database.connection import init_schema
from src.database.models import TaskRepository
from src.tools.task_tools import add_task_handler, list_tasks_handler

@pytest.fixture
async def db():
    """In-memory database for integration tests."""
    async with aiosqlite.connect(":memory:") as db:
        await init_schema(db)
        yield db

@pytest.fixture
async def repository(db):
    return TaskRepository(db)

@pytest.mark.asyncio
async def test_add_task_persists_to_database(repository, monkeypatch):
    """IT-ADD-001: Add task persists to database."""
    monkeypatch.setattr("src.tools.task_tools.repository", repository)
    
    result = await add_task_handler({"title": "Buy groceries"})
    
    # Verify task is in database
    task = await repository.get_by_id(result["task"]["id"])
    assert task is not None
    assert task.title == "Buy groceries"
    assert task.completed is False

@pytest.mark.asyncio
async def test_list_tasks_returns_all_tasks(repository, monkeypatch):
    """IT-LIST-001: List returns all tasks."""
    monkeypatch.setattr("src.tools.task_tools.repository", repository)
    
    # Add some tasks
    await repository.create("Task 1")
    await repository.create("Task 2")
    await repository.create("Task 3")
    
    result = await list_tasks_handler({})
    
    assert result["total"] == 3
    assert len(result["tasks"]) == 3
```

### 9.3 Schema Test Example

```python
# tests/unit/test_schemas.py
import pytest
from pydantic import ValidationError

from src.tools.schemas import TaskCreate, Task, ListTasksInput

class TestTaskCreate:
    """Tests for TaskCreate schema."""
    
    def test_valid_task_with_title_only(self):
        """UT-SCH-001: Valid task creation with title only."""
        task = TaskCreate(title="Buy groceries")
        assert task.title == "Buy groceries"
        assert task.parent_id is None
    
    def test_reject_empty_title(self):
        """UT-SCH-003: Reject empty title."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")
        
        errors = exc_info.value.errors()
        assert any(e["type"] == "string_too_short" for e in errors)
    
    def test_strip_whitespace_from_title(self):
        """UT-SCH-008: Strip whitespace from title."""
        task = TaskCreate(title="  Buy groceries  ")
        assert task.title == "Buy groceries"
    
    def test_reject_negative_parent_id(self):
        """UT-SCH-006: Reject negative parent_id."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", parent_id=-1)

class TestListTasksInput:
    """Tests for ListTasksInput schema."""
    
    def test_default_filter_is_all(self):
        """UT-SCH-020: ListTasksInput default filter."""
        input = ListTasksInput()
        assert input.filter == "all"
    
    def test_invalid_filter_rejected(self):
        """UT-SCH-022: ListTasksInput invalid filter."""
        with pytest.raises(ValidationError):
            ListTasksInput(filter="invalid")
```

---

*Document prepared for ChatGPT ToDo App test implementation. Last updated January 2026.*
