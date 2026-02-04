from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import ValidationError

from .schemas import (
    AddTaskInput,
    CompleteTaskInput,
    DecomposeTaskInput,
    DeleteTaskInput,
    ErrorCode,
    ListTasksInput,
    ToolError,
)

if TYPE_CHECKING:
    from src.database.models import TaskRepository

logger = logging.getLogger(__name__)


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} does not exist")


def _error_response(code: ErrorCode, message: str, details: dict | None = None) -> dict:
    """Build a standardized error response."""
    return {"error": ToolError(code=code, message=message, details=details).model_dump()}


async def add_task_handler(args: dict, repo: TaskRepository) -> dict:
    """Create a new task or subtask."""
    validated = AddTaskInput(**args)

    if validated.parent_id is not None:
        parent = await repo.get_by_id(validated.parent_id)
        if parent is None:
            raise TaskNotFoundError(validated.parent_id)

    task = await repo.create(validated.title, parent_id=validated.parent_id)
    return {
        "task": task,
        "ui": f"<inline-card>Task created: {task['title']}</inline-card>",
    }


async def list_tasks_handler(args: dict, repo: TaskRepository) -> dict:
    """Retrieve tasks with optional filtering."""
    validated = ListTasksInput(**args)

    tasks = await repo.get_all(filter=validated.filter, parent_id=validated.parent_id)
    return {
        "tasks": tasks,
        "total": len(tasks),
        "filter_applied": validated.filter,
        "ui": f"<inline-card>Found {len(tasks)} task(s)</inline-card>",
    }


async def complete_task_handler(args: dict, repo: TaskRepository) -> dict:
    """Mark a task as completed."""
    validated = CompleteTaskInput(**args)

    task = await repo.get_by_id(validated.task_id)
    if task is None:
        raise TaskNotFoundError(validated.task_id)

    updated = await repo.update_completed(validated.task_id, completed=True)
    return {
        "task": updated,
        "ui": f"<inline-card>Task completed: {updated['title']}</inline-card>",
    }


async def delete_task_handler(args: dict, repo: TaskRepository) -> dict:
    """Delete a task and its subtasks."""
    validated = DeleteTaskInput(**args)

    task = await repo.get_by_id(validated.task_id)
    if task is None:
        raise TaskNotFoundError(validated.task_id)

    subtasks = await repo.get_all(parent_id=validated.task_id)
    subtasks_count = len(subtasks)

    await repo.delete(validated.task_id)
    return {
        "deleted": True,
        "task_id": validated.task_id,
        "subtasks_deleted": subtasks_count,
        "ui": f"<inline-card>Task deleted</inline-card>",
    }


async def decompose_task_handler(args: dict, repo: TaskRepository) -> dict:
    """Break down a task into subtasks."""
    validated = DecomposeTaskInput(**args)

    parent = await repo.get_by_id(validated.task_id)
    if parent is None:
        raise TaskNotFoundError(validated.task_id)

    subtasks = await repo.create_subtasks(validated.task_id, validated.subtask_titles)
    return {
        "parent_task": parent,
        "subtasks": subtasks,
        "ui": f"<inline-card>Created {len(subtasks)} subtask(s) for: {parent['title']}</inline-card>",
    }


async def handle_tool_call(name: str, args: dict, repo: TaskRepository) -> dict:
    """Dispatch a tool call to the appropriate handler with error handling."""
    handlers = {
        "add_task": add_task_handler,
        "list_tasks": list_tasks_handler,
        "complete_task": complete_task_handler,
        "delete_task": delete_task_handler,
        "decompose_task": decompose_task_handler,
    }

    handler = handlers.get(name)
    if handler is None:
        return _error_response(
            ErrorCode.VALIDATION_ERROR,
            f"Unknown tool: {name}",
            details={"tool_name": name},
        )

    try:
        return await handler(args, repo)
    except TaskNotFoundError as e:
        return _error_response(
            ErrorCode.TASK_NOT_FOUND,
            str(e),
            details={"task_id": e.task_id},
        )
    except ValidationError as e:
        return _error_response(
            ErrorCode.VALIDATION_ERROR,
            "Invalid input",
            details={"errors": e.errors()},
        )
    except Exception as e:
        logger.exception("Unexpected error in tool call")
        return _error_response(
            ErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred",
        )
