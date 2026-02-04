from datetime import datetime

import pytest
from pydantic import ValidationError

from src.tools.schemas import (
    AddTaskInput,
    CompleteTaskInput,
    DeleteTaskInput,
    DecomposeTaskInput,
    ErrorCode,
    ListTasksInput,
    Task,
    TaskCreate,
    ToolError,
)


# --- Error Handling ---


class TestErrorCode:
    def test_values(self):
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.TASK_NOT_FOUND.value == "TASK_NOT_FOUND"
        assert ErrorCode.DATABASE_ERROR.value == "DATABASE_ERROR"
        assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"


class TestToolError:
    def test_minimal(self):
        err = ToolError(code=ErrorCode.TASK_NOT_FOUND, message="Not found")
        assert err.code == ErrorCode.TASK_NOT_FOUND
        assert err.message == "Not found"
        assert err.details is None

    def test_with_details(self):
        err = ToolError(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid input",
            details={"field": "title"},
        )
        assert err.details == {"field": "title"}


# --- Task Models ---


class TestTaskCreate:
    def test_valid(self):
        tc = TaskCreate(title="Buy milk")
        assert tc.title == "Buy milk"
        assert tc.parent_id is None

    def test_with_parent_id(self):
        tc = TaskCreate(title="Subtask", parent_id=5)
        assert tc.parent_id == 5

    def test_strips_whitespace(self):
        tc = TaskCreate(title="  padded  ")
        assert tc.title == "padded"

    def test_empty_title_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_whitespace_only_title_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="   ")

    def test_title_too_long_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="x" * 501)

    def test_parent_id_zero_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", parent_id=0)

    def test_parent_id_negative_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", parent_id=-1)


class TestTask:
    def test_from_dict(self):
        t = Task(
            id=1,
            title="Test",
            completed=False,
            created_at=datetime(2026, 1, 1, 12, 0, 0),
        )
        assert t.id == 1
        assert t.title == "Test"
        assert t.completed is False
        assert t.parent_id is None
        assert t.subtasks == []

    def test_with_subtasks(self):
        sub = Task(id=2, title="Sub", completed=False, created_at=datetime.now())
        parent = Task(
            id=1,
            title="Parent",
            completed=False,
            created_at=datetime.now(),
            subtasks=[sub],
        )
        assert len(parent.subtasks) == 1
        assert parent.subtasks[0].title == "Sub"

    def test_from_attributes_config(self):
        assert Task.model_config.get("from_attributes") is True


# --- Tool Input Schemas ---


class TestAddTaskInput:
    def test_valid(self):
        inp = AddTaskInput(title="Task")
        assert inp.title == "Task"
        assert inp.parent_id is None

    def test_with_parent_id(self):
        inp = AddTaskInput(title="Sub", parent_id=1)
        assert inp.parent_id == 1

    def test_strips_whitespace(self):
        inp = AddTaskInput(title="  spaced  ")
        assert inp.title == "spaced"

    def test_empty_title_fails(self):
        with pytest.raises(ValidationError):
            AddTaskInput(title="")

    def test_whitespace_only_title_fails(self):
        with pytest.raises(ValidationError):
            AddTaskInput(title="   ")

    def test_title_max_length(self):
        inp = AddTaskInput(title="x" * 500)
        assert len(inp.title) == 500

    def test_title_too_long_fails(self):
        with pytest.raises(ValidationError):
            AddTaskInput(title="x" * 501)


class TestListTasksInput:
    def test_defaults(self):
        inp = ListTasksInput()
        assert inp.filter == "all"
        assert inp.parent_id is None

    def test_filter_all(self):
        inp = ListTasksInput(filter="all")
        assert inp.filter == "all"

    def test_filter_complete(self):
        inp = ListTasksInput(filter="complete")
        assert inp.filter == "complete"

    def test_filter_incomplete(self):
        inp = ListTasksInput(filter="incomplete")
        assert inp.filter == "incomplete"

    def test_filter_invalid_fails(self):
        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(filter="invalid")
        assert "filter must be" in str(exc_info.value)

    def test_with_parent_id(self):
        inp = ListTasksInput(parent_id=5)
        assert inp.parent_id == 5

    def test_parent_id_zero_fails(self):
        with pytest.raises(ValidationError):
            ListTasksInput(parent_id=0)


class TestCompleteTaskInput:
    def test_valid(self):
        inp = CompleteTaskInput(task_id=1)
        assert inp.task_id == 1

    def test_missing_task_id_fails(self):
        with pytest.raises(ValidationError):
            CompleteTaskInput()

    def test_task_id_zero_fails(self):
        with pytest.raises(ValidationError):
            CompleteTaskInput(task_id=0)

    def test_task_id_negative_fails(self):
        with pytest.raises(ValidationError):
            CompleteTaskInput(task_id=-5)


class TestDeleteTaskInput:
    def test_valid(self):
        inp = DeleteTaskInput(task_id=42)
        assert inp.task_id == 42

    def test_missing_task_id_fails(self):
        with pytest.raises(ValidationError):
            DeleteTaskInput()

    def test_task_id_zero_fails(self):
        with pytest.raises(ValidationError):
            DeleteTaskInput(task_id=0)


class TestDecomposeTaskInput:
    def test_valid(self):
        inp = DecomposeTaskInput(task_id=1, subtask_titles=["A", "B", "C"])
        assert inp.task_id == 1
        assert inp.subtask_titles == ["A", "B", "C"]

    def test_strips_whitespace_from_titles(self):
        inp = DecomposeTaskInput(task_id=1, subtask_titles=["  A  ", "B", "  C"])
        assert inp.subtask_titles == ["A", "B", "C"]

    def test_filters_empty_titles(self):
        inp = DecomposeTaskInput(task_id=1, subtask_titles=["A", "   ", "B"])
        assert inp.subtask_titles == ["A", "B"]

    def test_missing_task_id_fails(self):
        with pytest.raises(ValidationError):
            DecomposeTaskInput(subtask_titles=["A"])

    def test_missing_subtask_titles_fails(self):
        with pytest.raises(ValidationError):
            DecomposeTaskInput(task_id=1)

    def test_empty_subtask_titles_fails(self):
        with pytest.raises(ValidationError):
            DecomposeTaskInput(task_id=1, subtask_titles=[])

    def test_max_subtask_titles(self):
        titles = [f"Task {i}" for i in range(10)]
        inp = DecomposeTaskInput(task_id=1, subtask_titles=titles)
        assert len(inp.subtask_titles) == 10

    def test_too_many_subtask_titles_fails(self):
        titles = [f"Task {i}" for i in range(11)]
        with pytest.raises(ValidationError):
            DecomposeTaskInput(task_id=1, subtask_titles=titles)
