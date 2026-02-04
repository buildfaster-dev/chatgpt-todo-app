# CLAUDE.md - ChatGPT ToDo App

## Project Overview

A ChatGPT-integrated ToDo application using the OpenAI Apps SDK with MCP (Model Context Protocol) in Python. Users manage tasks conversationally within ChatGPT, with AI-assisted task decomposition. This is a **learning project** demonstrating MCP server patterns, tool definitions, and conversational UI.

**Stack:** Python 3.10+ | MCP SDK | SQLite | Pydantic 2.x | uvicorn  
**Status:** In Development (Week 1 of 4)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ChatGPT Client                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ MCP Protocol (Streamable HTTP)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   MCP Server (Python)                       │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────────────┐  │
│  │  Tools    │  │  Database │  │   UI Components         │  │
│  │  Handler  │  │  Layer    │  │   (HTML Templates)      │  │
│  └─────┬─────┘  └─────┬─────┘  └────────────┬────────────┘  │
│        └──────────────┼─────────────────────┘               │
│                       ▼                                     │
│                 ┌───────────┐                               │
│                 │  SQLite   │                               │
│                 │ tasks.db  │                               │
│                 └───────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:** User message → ChatGPT → MCP call_tool → Tool Handler → Database → UI Component → Response

## Directory Structure

```
chatgpt-todo-app/
├── docs/
│   ├── prompts/            # Prompts used to generate docs
│   ├── PRD.md              # Product requirements
│   ├── TDD.md              # Technical design (includes ADRs)
│   ├── C4-diagrams.md      # Architecture diagrams
│   └── test-spec.md        # Test specification
├── src/
│   ├── __init__.py
│   ├── server.py           # MCP server entry point
│   ├── config.py           # Environment configuration
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── task_tools.py   # Tool handlers (add, list, complete, delete, decompose)
│   │   └── schemas.py      # Pydantic input/output schemas
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py   # SQLite connection management
│   │   └── models.py       # TaskRepository with CRUD operations
│   └── ui/
│       ├── __init__.py
│       └── components.py   # Inline card HTML generators
├── tests/
│   ├── conftest.py         # Shared fixtures (test_db, task_repo, sample_task)
│   ├── unit/               # Schema, model, component tests
│   └── integration/        # Tool handler + database tests
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Key Files

| File | Purpose | When to Modify |
|------|---------|----------------|
| `src/server.py` | MCP server setup, tool registration | Adding new tools |
| `src/tools/task_tools.py` | Tool handler implementations | Changing tool behavior |
| `src/tools/schemas.py` | Pydantic models for validation | Adding/changing tool parameters |
| `src/database/models.py` | TaskRepository with SQL queries | Database operations |
| `src/database/connection.py` | SQLite connection, schema init | Schema migrations |
| `src/ui/components.py` | HTML inline card generators | UI changes |
| `src/config.py` | Environment variables | New configuration |

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start dev server
uvicorn src.server:app --host localhost --port 8000 --reload

# Run all tests
pytest

# Run with coverage (target: 70%)
pytest --cov=src --cov-report=term-missing

# Run unit tests only
pytest tests/unit/

# Lint
ruff check src/

# Type check
mypy src/

# Open SQLite CLI
sqlite3 ~/.chatgpt-todo/tasks.db
```

## Environment Variables

```bash
DATABASE_PATH=~/.chatgpt-todo/tasks.db  # SQLite file location
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
LOG_LEVEL=DEBUG  # DEBUG | INFO | WARNING | ERROR
```

## Code Conventions

### Naming
- **Files:** snake_case (`task_tools.py`)
- **Classes:** PascalCase (`TaskRepository`)
- **Functions/Variables:** snake_case (`add_task_handler`)
- **Constants:** UPPER_SNAKE_CASE (`DATABASE_PATH`)

### Patterns
- **Async everywhere:** All handlers and DB operations use `async/await`
- **Pydantic for validation:** All tool inputs/outputs are Pydantic models
- **Layered architecture:** Tools → Database → UI (no cross-layer imports)
- **Parameterized SQL:** Never use f-strings for queries

### Avoid
- ❌ Synchronous database calls (blocks event loop)
- ❌ String interpolation in SQL queries
- ❌ Direct SQLite access from tool handlers (use TaskRepository)
- ❌ Hardcoded configuration values

## MCP Tools Reference

| Tool | Parameters | Returns |
|------|------------|---------|
| `add_task` | `title: str`, `parent_id?: int` | Task + inline card |
| `list_tasks` | `filter?: "all"\|"complete"\|"incomplete"`, `parent_id?: int` | Task array + list card |
| `complete_task` | `task_id: int` | Updated task + confirmation |
| `delete_task` | `task_id: int` | Deletion confirmation |
| `decompose_task` | `task_id: int`, `subtask_titles: list[str]` | Parent + subtasks + hierarchy card |

## Database Schema

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) > 0),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    parent_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_id);
```

## Common Patterns

### Adding a New Tool

1. Define schema in `src/tools/schemas.py`:
```python
class NewToolInput(BaseModel):
    param: str = Field(..., description="Parameter description")
```

2. Add handler in `src/tools/task_tools.py`:
```python
async def new_tool_handler(args: dict, repo: TaskRepository) -> dict:
    validated = NewToolInput(**args)
    result = await repo.some_operation(validated.param)
    return {"data": result, "ui": render_some_card(result)}
```

3. Register in `src/server.py`:
```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [..., new_tool]
```

### Adding a Database Operation

```python
# In src/database/models.py
async def new_operation(self, param: str) -> Task:
    async with self.db.execute(
        "SELECT * FROM tasks WHERE title LIKE ?",
        (f"%{param}%",)
    ) as cursor:
        row = await cursor.fetchone()
        return Task(**row) if row else None
```

### Creating UI Components

```python
# In src/ui/components.py
def render_custom_card(task: Task) -> str:
    return f"""
    <inline-card>
        <div class="task-card">
            <span class="title">{html.escape(task.title)}</span>
            <span class="status">{'✓' if task.completed else '○'}</span>
        </div>
    </inline-card>
    """
```

### Writing Tests

```python
# Unit test
def test_schema_validation():
    with pytest.raises(ValidationError):
        TaskCreate(title="")

# Integration test
@pytest.mark.asyncio
async def test_add_task(task_repo):
    result = await add_task_handler({"title": "Test"}, repo=task_repo)
    assert result["task"]["title"] == "Test"
    assert "ui" in result
```

## Implementation Order

1. [x] Dependencies (pyproject.toml, requirements.txt)
2. [x] Configuration (config.py, .env.example)
3. [x] Database layer (connection.py, models.py)
4. [x] Tools layer (schemas.py, task_tools.py)
5. [x] UI layer (components.py)
6. [ ] Server (server.py)
7. [ ] Tests

## Error Handling

All tools return errors in this format:
```python
{
    "error": {
        "code": "TASK_NOT_FOUND",  # VALIDATION_ERROR | DATABASE_ERROR | INTERNAL_ERROR
        "message": "Task with ID 99 does not exist",
        "details": {"task_id": 99}
    }
}
```

## Reference Links

- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk/)
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Apps SDK UI Guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)
