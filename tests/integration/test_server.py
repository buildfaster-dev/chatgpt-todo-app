import json
from unittest.mock import MagicMock

import pytest

from src.database.models import TaskRepository
from src.server import (
    _get_repo,
    add_task,
    complete_task,
    decompose_task,
    delete_task,
    lifespan,
    list_tasks,
    mcp,
)

EXPECTED_TOOLS = {"add_task", "list_tasks", "complete_task", "delete_task", "decompose_task"}


@pytest.fixture
def ctx(task_repo):
    """Mock MCP Context backed by the test database."""
    mock = MagicMock()
    mock.request_context.lifespan_context = task_repo
    return mock


class TestServerConfig:
    def test_server_name(self):
        assert mcp.name == "ChatGPT ToDo App"

    def test_server_has_instructions(self):
        assert mcp.instructions is not None
        assert "tasks" in mcp.instructions.lower()


class TestToolRegistration:
    def test_all_tools_registered(self):
        tool_names = set(mcp._tool_manager._tools.keys())
        assert tool_names == EXPECTED_TOOLS

    def test_tool_count(self):
        assert len(mcp._tool_manager._tools) == 5


class TestToolSchemas:
    def _get_tool(self, name):
        return mcp._tool_manager._tools[name]

    def test_add_task_has_required_params(self):
        props = self._get_tool("add_task").parameters["properties"]
        assert "title" in props
        assert "parent_id" in props

    def test_list_tasks_has_filter_param(self):
        props = self._get_tool("list_tasks").parameters["properties"]
        assert "filter" in props
        assert "parent_id" in props

    def test_complete_task_has_task_id(self):
        props = self._get_tool("complete_task").parameters["properties"]
        assert "task_id" in props

    def test_delete_task_has_task_id(self):
        props = self._get_tool("delete_task").parameters["properties"]
        assert "task_id" in props

    def test_decompose_task_has_required_params(self):
        props = self._get_tool("decompose_task").parameters["properties"]
        assert "task_id" in props
        assert "subtask_titles" in props


class TestAsgiApp:
    def test_app_is_starlette_instance(self):
        from src.server import app
        from starlette.applications import Starlette

        assert isinstance(app, Starlette)


class TestGetRepo:
    def test_returns_repo(self, ctx, task_repo):
        assert _get_repo(ctx) is task_repo


class TestLifespan:
    async def test_yields_task_repository(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.server.DATABASE_PATH", tmp_path / "test.db")
        async with lifespan(MagicMock()) as repo:
            assert isinstance(repo, TaskRepository)

    async def test_creates_parent_directory(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.server.DATABASE_PATH", tmp_path / "sub" / "test.db")
        async with lifespan(MagicMock()):
            assert (tmp_path / "sub").exists()


class TestToolFunctions:
    async def test_add_task(self, ctx):
        result = json.loads(await add_task("Buy milk", ctx))
        assert result["task"]["title"] == "Buy milk"

    async def test_add_task_with_parent(self, ctx, sample_task):
        result = json.loads(await add_task("Sub", ctx, parent_id=sample_task["id"]))
        assert result["task"]["parent_id"] == sample_task["id"]

    async def test_list_tasks(self, ctx):
        await add_task("A", ctx)
        result = json.loads(await list_tasks(ctx))
        assert result["total"] == 1

    async def test_list_tasks_with_filter(self, ctx):
        result = json.loads(await list_tasks(ctx, filter="incomplete"))
        assert result["filter_applied"] == "incomplete"

    async def test_list_tasks_with_parent_id(self, ctx, sample_task):
        await add_task("Child", ctx, parent_id=sample_task["id"])
        result = json.loads(await list_tasks(ctx, parent_id=sample_task["id"]))
        assert result["total"] == 1

    async def test_complete_task(self, ctx, sample_task):
        result = json.loads(await complete_task(sample_task["id"], ctx))
        assert result["task"]["completed"] == 1

    async def test_delete_task(self, ctx, sample_task):
        result = json.loads(await delete_task(sample_task["id"], ctx))
        assert result["deleted"] is True

    async def test_decompose_task(self, ctx, sample_task):
        result = json.loads(await decompose_task(sample_task["id"], ["A", "B"], ctx))
        assert len(result["subtasks"]) == 2
