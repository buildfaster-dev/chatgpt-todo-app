"""UI component stubs for inline card generation.

These will be implemented in the UI layer phase. For now, they return
simple placeholder HTML that can be used during development.
"""

from __future__ import annotations


def render_task_card(task: dict) -> str:
    """Render a single task as an inline card."""
    status = "✓" if task.get("completed") else "○"
    return f"<inline-card>{status} {task['title']}</inline-card>"


def render_task_list(tasks: list[dict]) -> str:
    """Render a list of tasks as an inline card."""
    if not tasks:
        return "<inline-card>No tasks found</inline-card>"
    count = len(tasks)
    return f"<inline-card>Found {count} task(s)</inline-card>"


def render_confirmation(message: str, task: dict | None = None) -> str:
    """Render a confirmation message as an inline card."""
    return f"<inline-card>{message}</inline-card>"


def render_task_hierarchy(parent: dict, subtasks: list[dict]) -> str:
    """Render a parent task with its subtasks as an inline card."""
    count = len(subtasks)
    return f"<inline-card>{parent['title']} ({count} subtask(s))</inline-card>"
