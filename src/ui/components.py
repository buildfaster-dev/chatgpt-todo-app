"""UI components for inline card generation.

Generates HTML for inline cards following Apps SDK UI guidelines.
Supports light/dark mode via CSS variables and includes proper HTML escaping.
"""

from __future__ import annotations

import html
from typing import Any

# CSS styles with light/dark mode support via CSS variables
_STYLES = """
<style>
.task-card {
    font-family: system-ui, -apple-system, sans-serif;
    padding: 12px 16px;
    border-radius: 8px;
    background: var(--card-bg, #ffffff);
    border: 1px solid var(--card-border, #e0e0e0);
    color: var(--card-text, #1a1a1a);
}
.task-card .title {
    font-weight: 500;
}
.task-card .status {
    margin-right: 8px;
    color: var(--status-color, #666);
}
.task-card .status.completed {
    color: var(--status-completed, #22c55e);
}
.task-card .meta {
    font-size: 0.875em;
    color: var(--card-meta, #666);
    margin-top: 4px;
}
.task-list {
    font-family: system-ui, -apple-system, sans-serif;
}
.task-list .header {
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--card-text, #1a1a1a);
}
.task-list .item {
    padding: 8px 12px;
    border-radius: 6px;
    background: var(--card-bg, #ffffff);
    border: 1px solid var(--card-border, #e0e0e0);
    margin-bottom: 6px;
    color: var(--card-text, #1a1a1a);
}
.task-list .item:last-child {
    margin-bottom: 0;
}
.task-list .empty {
    color: var(--card-meta, #666);
    font-style: italic;
}
.confirmation {
    font-family: system-ui, -apple-system, sans-serif;
    padding: 12px 16px;
    border-radius: 8px;
    background: var(--confirm-bg, #f0fdf4);
    border: 1px solid var(--confirm-border, #86efac);
    color: var(--confirm-text, #166534);
}
.hierarchy {
    font-family: system-ui, -apple-system, sans-serif;
}
.hierarchy .parent {
    font-weight: 600;
    padding: 12px 16px;
    border-radius: 8px 8px 0 0;
    background: var(--card-bg, #ffffff);
    border: 1px solid var(--card-border, #e0e0e0);
    border-bottom: none;
    color: var(--card-text, #1a1a1a);
}
.hierarchy .subtasks {
    padding: 8px 16px 12px 32px;
    border-radius: 0 0 8px 8px;
    background: var(--subtask-bg, #f9fafb);
    border: 1px solid var(--card-border, #e0e0e0);
}
.hierarchy .subtask {
    padding: 6px 0;
    color: var(--card-text, #1a1a1a);
}
.hierarchy .subtask:before {
    content: "└ ";
    color: var(--card-meta, #666);
}
@media (prefers-color-scheme: dark) {
    .task-card, .task-list .item, .hierarchy .parent {
        --card-bg: #1f1f1f;
        --card-border: #333;
        --card-text: #e5e5e5;
        --card-meta: #999;
        --status-color: #999;
    }
    .confirmation {
        --confirm-bg: #14532d;
        --confirm-border: #22c55e;
        --confirm-text: #bbf7d0;
    }
    .hierarchy .subtasks {
        --subtask-bg: #171717;
    }
}
</style>
"""


def render_task_card(task: dict[str, Any]) -> str:
    """Render a single task as an inline card."""
    title = html.escape(task["title"])
    completed = task.get("completed", False)
    status_class = "status completed" if completed else "status"
    status_icon = "✓" if completed else "○"

    return f"""<inline-card>
{_STYLES}
<div class="task-card">
    <span class="{status_class}">{status_icon}</span>
    <span class="title">{title}</span>
</div>
</inline-card>"""


def render_task_list(tasks: list[dict[str, Any]]) -> str:
    """Render a list of tasks as an inline card."""
    if not tasks:
        return f"""<inline-card>
{_STYLES}
<div class="task-list">
    <div class="empty">No tasks found</div>
</div>
</inline-card>"""

    items = []
    for task in tasks:
        title = html.escape(task["title"])
        completed = task.get("completed", False)
        status = "✓" if completed else "○"
        items.append(f'<div class="item"><span class="status">{status}</span> {title}</div>')

    items_html = "\n    ".join(items)
    count = len(tasks)

    return f"""<inline-card>
{_STYLES}
<div class="task-list">
    <div class="header">{count} task(s)</div>
    {items_html}
</div>
</inline-card>"""


def render_confirmation(message: str, task: dict[str, Any] | None = None) -> str:
    """Render a confirmation message as an inline card."""
    escaped_message = html.escape(message)

    task_info = ""
    if task:
        title = html.escape(task["title"])
        task_info = f'<div class="meta">Task: {title}</div>'

    return f"""<inline-card>
{_STYLES}
<div class="confirmation">
    <div>{escaped_message}</div>
    {task_info}
</div>
</inline-card>"""


def render_task_hierarchy(parent: dict[str, Any], subtasks: list[dict[str, Any]]) -> str:
    """Render a parent task with its subtasks as an inline card."""
    parent_title = html.escape(parent["title"])

    subtask_items = []
    for subtask in subtasks:
        title = html.escape(subtask["title"])
        completed = subtask.get("completed", False)
        status = "✓" if completed else "○"
        subtask_items.append(f'<div class="subtask">{status} {title}</div>')

    subtasks_html = "\n        ".join(subtask_items) if subtask_items else '<div class="subtask">No subtasks</div>'

    return f"""<inline-card>
{_STYLES}
<div class="hierarchy">
    <div class="parent">{parent_title}</div>
    <div class="subtasks">
        {subtasks_html}
    </div>
</div>
</inline-card>"""
