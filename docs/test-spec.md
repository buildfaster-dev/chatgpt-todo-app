# Test Specification Document

## ChatGPT ToDo App with AI Task Decomposition

| Document Version | 1.0 |
|------------------|-----|
| Last Updated | January 2026 |
| Related PRD | PRD v1.0 |
| Related TDD | TDD v1.0 |

---

## 1. Test Strategy Overview

### Testing Pyramid

| Level | Ratio | Focus |
|-------|-------|-------|
| Unit | 70% | Individual functions, models, validators |
| Integration | 30% | Tool handlers with database, MCP request/response cycle |
| E2E | 0% | Skipped for learning project |

### Coverage & Tools

| Aspect | Target/Tool |
|--------|-------------|
| Coverage Target | 70% line coverage |
| Test Framework | pytest 8.x |
| Async Testing | pytest-asyncio |
| Coverage Tool | pytest-cov |
| Mocking | pytest (built-in fixtures) |

---

## 2. Unit Tests Specification

### 2.1 Database Layer (`database/models.py`)

| ID | Description | Input | Expected |
|----|-------------|-------|----------|
| DB-01 | Create task successfully | `title="Buy groceries"` | Task with id, title, completed=False, created_at |
| DB-02 | Create subtask with parent_id | `title="Buy milk", parent_id=1` | Task with parent_id=1 |
| DB-03 | Create task with empty title fails | `title=""` | Raises ValidationError |
| DB-04 | Get task by non-existent ID | `task_id=999` | Returns None |
| DB-05 | Delete task cascades to subtasks | Parent with 2 subtasks deleted | All 3 records removed |

### 2.2 Tools Layer (`tools/task_tools.py`)

| ID | Description | Input | Expected |
|----|-------------|-------|----------|
| TL-01 | add_task returns task and UI | `{"title": "Test"}` | `{task: {...}, ui: "<inline-card>..."}` |
| TL-02 | list_tasks with filter | `{"filter": "incomplete"}` | Only incomplete tasks returned |
| TL-03 | complete_task on non-existent ID | `{"task_id": 999}` | Error with code TASK_NOT_FOUND |
| TL-04 | delete_task returns confirmation | `{"task_id": 1}` | `{deleted: true, task_id: 1}` |
| TL-05 | decompose_task creates subtasks | `{"task_id": 1, "subtask_titles": ["A", "B"]}` | 2 subtasks with parent_id=1 |

### 2.3 Pydantic Schemas (`tools/schemas.py`)

| ID | Description | Input | Expected |
|----|-------------|-------|----------|
| SC-01 | TaskCreate validates title length | `title="x" * 501` | Raises ValidationError |
| SC-02 | TaskCreate strips whitespace | `title="  Test  "` | `title="Test"` |
| SC-03 | AddTaskInput accepts optional parent_id | `{"title": "Test"}` | Valid, parent_id=None |
| SC-04 | CompleteTaskInput requires task_id | `{}` | Raises ValidationError |

### 2.4 UI Components (`ui/components.py`)

| ID | Description | Input | Expected |
|----|-------------|-------|----------|
| UI-01 | render_task_card includes title | Task(title="Test") | HTML contains "Test" |
| UI-02 | render_task_card shows completion status | Task(completed=True) | HTML contains status indicator |
| UI-03 | render_task_list handles empty list | `[]` | HTML with empty state message |
| UI-04 | render_task_hierarchy shows parent and children | Parent + 2 subtasks | Hierarchical HTML structure |

---

## 3. Integration Tests Specification

| ID | Test Flow | Components | Expected Outcome |
|----|-----------|------------|------------------|
| INT-01 | Add task via tool handler | Tools → Database → UI | Task persisted, UI card returned |
| INT-02 | List tasks after adding multiple | Tools → Database | All tasks returned with correct data |
| INT-03 | Complete task updates database | Tools → Database | Task.completed=True in DB |
| INT-04 | Delete task removes from database | Tools → Database | Task not found after deletion |
| INT-05 | Filter tasks by completion status | Tools → Database | Only matching tasks returned |
| INT-06 | Create subtask with valid parent_id | Tools → Database | Subtask linked to parent |
| INT-07 | Decompose task creates hierarchy | Tools → Database → UI | Parent has subtasks, hierarchy UI rendered |
| INT-08 | Delete parent cascades to subtasks | Tools → Database | Parent and all subtasks deleted |
| INT-09 | MCP list_tools returns all tools | Server → Tools | 5 tools with correct schemas |
| INT-10 | MCP call_tool invokes correct handler | Server → Tools | Handler executed, result returned |

---

## 4. Fixtures

### 4.1 Database Fixtures

```python
# tests/conftest.py
import pytest
import aiosqlite
from src.database.connection import init_db
from src.database.models import TaskRepository

@pytest.fixture
async def test_db():
    """In-memory SQLite database for isolated tests."""
    async with aiosqlite.connect(":memory:") as db:
        await init_db(db)
        yield db

@pytest.fixture
async def task_repo(test_db):
    """TaskRepository instance with test database."""
    return TaskRepository(test_db)

@pytest.fixture
async def sample_task(task_repo):
    """Pre-created task for tests that need existing data."""
    return await task_repo.create(title="Sample Task")

@pytest.fixture
async def task_with_subtasks(task_repo):
    """Parent task with two subtasks."""
    parent = await task_repo.create(title="Parent Task")
    sub1 = await task_repo.create(title="Subtask 1", parent_id=parent.id)
    sub2 = await task_repo.create(title="Subtask 2", parent_id=parent.id)
    return {"parent": parent, "subtasks": [sub1, sub2]}
```

### 4.2 Mock MCP Request Fixture

```python
@pytest.fixture
def mock_tool_call():
    """Factory for creating MCP tool call requests."""
    def _create(tool_name: str, arguments: dict):
        return {
            "method": "call_tool",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
    return _create
```

---

## 5. Test Cases per User Story (P0)

### US-01: Add Task

| TC ID | Test Case | Acceptance Criteria Verified |
|-------|-----------|------------------------------|
| US01-TC01 | Add task with title "Buy groceries" creates task in DB | AC1, AC3, AC4 |
| US01-TC02 | Add task returns inline card with task details | AC3 |
| US01-TC03 | Add task with empty title returns validation error | AC1 (negative) |

### US-02: View All Tasks

| TC ID | Test Case | Acceptance Criteria Verified |
|-------|-----------|------------------------------|
| US02-TC01 | List tasks returns all tasks with title and status | AC2, AC3 |
| US02-TC02 | List tasks on empty database returns empty state UI | AC4 |
| US02-TC03 | List tasks shows correct completion status | AC3 |

### US-03: Mark Task Complete

| TC ID | Test Case | Acceptance Criteria Verified |
|-------|-----------|------------------------------|
| US03-TC01 | Complete task by ID updates status to true | AC2, AC4 |
| US03-TC02 | Complete task returns visual confirmation card | AC3 |
| US03-TC03 | Complete non-existent task returns error | AC2 (negative) |

### US-04: Delete Task

| TC ID | Test Case | Acceptance Criteria Verified |
|-------|-----------|------------------------------|
| US04-TC01 | Delete task by ID removes from database | AC2, AC4 |
| US04-TC02 | Delete task returns confirmation UI | AC3 |
| US04-TC03 | Delete parent task removes subtasks | AC2, AC4 |

### US-05: MCP Server Tools

| TC ID | Test Case | Acceptance Criteria Verified |
|-------|-----------|------------------------------|
| US05-TC01 | list_tools returns all 5 tools with schemas | AC1, AC2 |
| US05-TC02 | Each tool has description for model discovery | AC3 |
| US05-TC03 | call_tool with valid params executes handler | AC4 |

### US-06: SQLite Persistence

| TC ID | Test Case | Acceptance Criteria Verified |
|-------|-----------|------------------------------|
| US06-TC01 | Database created with correct schema on first run | AC1, AC2 |
| US06-TC02 | Task persists after database reconnection | AC3 |
| US06-TC03 | Database path configurable via environment variable | AC4 |

---

## 6. Sample Test Implementations

### Unit Test Example

```python
# tests/unit/test_schemas.py
import pytest
from pydantic import ValidationError
from src.tools.schemas import TaskCreate

def test_task_create_valid():
    """TC SC-03: TaskCreate accepts optional parent_id."""
    task = TaskCreate(title="Test Task")
    assert task.title == "Test Task"
    assert task.parent_id is None

def test_task_create_strips_whitespace():
    """TC SC-02: Title whitespace is stripped."""
    task = TaskCreate(title="  Test Task  ")
    assert task.title == "Test Task"

def test_task_create_rejects_empty_title():
    """TC SC-01 related: Empty title rejected."""
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="")
    assert "title" in str(exc_info.value)
```

### Integration Test Example

```python
# tests/integration/test_tools.py
import pytest
from src.tools.task_tools import add_task_handler, list_tasks_handler

@pytest.mark.asyncio
async def test_add_and_list_tasks(task_repo):
    """INT-02: List tasks after adding multiple."""
    # Add tasks
    await add_task_handler({"title": "Task 1"}, repo=task_repo)
    await add_task_handler({"title": "Task 2"}, repo=task_repo)
    
    # List all
    result = await list_tasks_handler({"filter": "all"}, repo=task_repo)
    
    assert len(result["tasks"]) == 2
    assert result["tasks"][0]["title"] == "Task 1"
    assert result["tasks"][1]["title"] == "Task 2"
    assert "ui" in result

@pytest.mark.asyncio
async def test_complete_task_updates_database(task_repo, sample_task):
    """INT-03: Complete task updates database."""
    from src.tools.task_tools import complete_task_handler
    
    result = await complete_task_handler(
        {"task_id": sample_task.id}, 
        repo=task_repo
    )
    
    assert result["task"]["completed"] is True
    
    # Verify in database
    updated = await task_repo.get_by_id(sample_task.id)
    assert updated.completed is True
```

---

## 7. Test Organization

```
tests/
├── conftest.py              # Shared fixtures (§4)
├── unit/
│   ├── test_schemas.py      # Pydantic validation (§2.3)
│   ├── test_models.py       # Task model (§2.1)
│   └── test_components.py   # UI rendering (§2.4)
└── integration/
    ├── test_tools.py        # Tool handlers (§2.2, §3)
    └── test_database.py     # Repository operations (§2.1)
```

---

## 8. Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run specific test file
pytest tests/integration/test_tools.py -v

# Run tests matching pattern
pytest -k "test_add_task"
```

---

*Document prepared for learning purposes. Target: 70% coverage with focus on critical paths.*
