import pytest

from src.tools.task_tools import (
    TaskNotFoundError,
    add_task_handler,
    complete_task_handler,
    decompose_task_handler,
    delete_task_handler,
    handle_tool_call,
    list_tasks_handler,
)


# --- add_task_handler ---


class TestAddTaskHandler:
    async def test_creates_task(self, task_repo):
        result = await add_task_handler({"title": "Buy milk"}, task_repo)
        assert result["task"]["title"] == "Buy milk"
        assert result["task"]["completed"] == 0
        assert "ui" in result

    async def test_creates_subtask(self, task_repo, sample_task):
        result = await add_task_handler(
            {"title": "Subtask", "parent_id": sample_task["id"]}, task_repo
        )
        assert result["task"]["parent_id"] == sample_task["id"]

    async def test_invalid_parent_raises(self, task_repo):
        with pytest.raises(TaskNotFoundError) as exc_info:
            await add_task_handler({"title": "Task", "parent_id": 999}, task_repo)
        assert exc_info.value.task_id == 999


# --- list_tasks_handler ---


class TestListTasksHandler:
    async def test_returns_all_tasks(self, task_repo, sample_task):
        result = await list_tasks_handler({}, task_repo)
        assert result["total"] == 1
        assert result["filter_applied"] == "all"
        assert "ui" in result

    async def test_filter_complete(self, task_repo, sample_task):
        await task_repo.update_completed(sample_task["id"], True)
        result = await list_tasks_handler({"filter": "complete"}, task_repo)
        assert result["total"] == 1

    async def test_filter_incomplete(self, task_repo, sample_task):
        result = await list_tasks_handler({"filter": "incomplete"}, task_repo)
        assert result["total"] == 1

    async def test_filter_by_parent(self, task_repo, sample_task):
        await task_repo.create("Child", parent_id=sample_task["id"])
        result = await list_tasks_handler({"parent_id": sample_task["id"]}, task_repo)
        assert result["total"] == 1

    async def test_empty_result(self, task_repo):
        result = await list_tasks_handler({}, task_repo)
        assert result["total"] == 0
        assert result["tasks"] == []


# --- complete_task_handler ---


class TestCompleteTaskHandler:
    async def test_completes_task(self, task_repo, sample_task):
        result = await complete_task_handler({"task_id": sample_task["id"]}, task_repo)
        assert result["task"]["completed"] == 1
        assert "ui" in result

    async def test_nonexistent_task_raises(self, task_repo):
        with pytest.raises(TaskNotFoundError) as exc_info:
            await complete_task_handler({"task_id": 999}, task_repo)
        assert exc_info.value.task_id == 999


# --- delete_task_handler ---


class TestDeleteTaskHandler:
    async def test_deletes_task(self, task_repo, sample_task):
        result = await delete_task_handler({"task_id": sample_task["id"]}, task_repo)
        assert result["deleted"] is True
        assert result["task_id"] == sample_task["id"]
        assert "ui" in result

    async def test_counts_subtasks_deleted(self, task_repo, sample_task):
        await task_repo.create_subtasks(sample_task["id"], ["A", "B"])
        result = await delete_task_handler({"task_id": sample_task["id"]}, task_repo)
        assert result["subtasks_deleted"] == 2

    async def test_nonexistent_task_raises(self, task_repo):
        with pytest.raises(TaskNotFoundError) as exc_info:
            await delete_task_handler({"task_id": 999}, task_repo)
        assert exc_info.value.task_id == 999


# --- decompose_task_handler ---


class TestDecomposeTaskHandler:
    async def test_creates_subtasks(self, task_repo, sample_task):
        result = await decompose_task_handler(
            {"task_id": sample_task["id"], "subtask_titles": ["A", "B", "C"]},
            task_repo,
        )
        assert result["parent_task"]["id"] == sample_task["id"]
        assert len(result["subtasks"]) == 3
        assert all(s["parent_id"] == sample_task["id"] for s in result["subtasks"])
        assert "ui" in result

    async def test_nonexistent_task_raises(self, task_repo):
        with pytest.raises(TaskNotFoundError) as exc_info:
            await decompose_task_handler(
                {"task_id": 999, "subtask_titles": ["A"]}, task_repo
            )
        assert exc_info.value.task_id == 999


# --- handle_tool_call ---


class TestHandleToolCall:
    async def test_dispatches_to_handler(self, task_repo):
        result = await handle_tool_call("add_task", {"title": "Test"}, task_repo)
        assert "task" in result
        assert result["task"]["title"] == "Test"

    async def test_unknown_tool_returns_error(self, task_repo):
        result = await handle_tool_call("unknown_tool", {}, task_repo)
        assert "error" in result
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert "unknown_tool" in result["error"]["message"].lower()

    async def test_task_not_found_returns_error(self, task_repo):
        result = await handle_tool_call("complete_task", {"task_id": 999}, task_repo)
        assert "error" in result
        assert result["error"]["code"] == "TASK_NOT_FOUND"
        assert result["error"]["details"]["task_id"] == 999

    async def test_validation_error_returns_error(self, task_repo):
        result = await handle_tool_call("add_task", {"title": ""}, task_repo)
        assert "error" in result
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert "errors" in result["error"]["details"]

    async def test_all_tools_dispatch(self, task_repo, sample_task):
        tools = [
            ("add_task", {"title": "New"}),
            ("list_tasks", {}),
            ("complete_task", {"task_id": sample_task["id"]}),
            ("decompose_task", {"task_id": sample_task["id"], "subtask_titles": ["X"]}),
            ("delete_task", {"task_id": sample_task["id"]}),
        ]
        for tool_name, args in tools:
            result = await handle_tool_call(tool_name, args, task_repo)
            assert "error" not in result, f"{tool_name} failed: {result}"
