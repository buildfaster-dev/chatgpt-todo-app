"""MCP server entry point.

Initializes the MCP server, registers all tools, and manages the
HTTP transport layer using FastMCP with Streamable HTTP.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from collections.abc import AsyncIterator
from typing import Any

from mcp.server.fastmcp import Context, FastMCP

from src.config import DATABASE_PATH, LOG_LEVEL, MCP_SERVER_HOST, MCP_SERVER_PORT
from src.database.connection import get_connection, init_db
from src.database.models import TaskRepository
from src.tools.task_tools import handle_tool_call

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(server: FastMCP[TaskRepository]) -> AsyncIterator[TaskRepository]:
    """Manage database connection lifecycle."""
    db_path = str(DATABASE_PATH)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    logger.info("Connecting to database: %s", db_path)
    db = await get_connection(db_path)
    await init_db(db)
    logger.info("Database initialized")

    try:
        yield TaskRepository(db)
    finally:
        logger.info("Closing database connection")
        await db.close()


mcp = FastMCP(
    name="ChatGPT ToDo App",
    instructions="Manage your tasks conversationally. You can add, list, complete, delete, and decompose tasks.",
    host=MCP_SERVER_HOST,
    port=MCP_SERVER_PORT,
    log_level=LOG_LEVEL,  # type: ignore[arg-type]
    lifespan=lifespan,
)


def _get_repo(ctx: Context[Any, Any, Any]) -> TaskRepository:
    """Retrieve the TaskRepository from the server lifespan context."""
    repo: TaskRepository = ctx.request_context.lifespan_context
    return repo


@mcp.tool()
async def add_task(
    title: str,
    ctx: Context[Any, Any, Any],
    parent_id: int | None = None,
) -> str:
    """Create a new task or subtask.

    Args:
        title: The task description (1-500 characters)
        parent_id: Optional parent task ID for creating subtasks
    """
    logger.info("add_task called: title=%r, parent_id=%s", title, parent_id)
    repo = _get_repo(ctx)
    args: dict[str, Any] = {"title": title}
    if parent_id is not None:
        args["parent_id"] = parent_id
    result = await handle_tool_call("add_task", args, repo)
    return json.dumps(result, default=str)


@mcp.tool()
async def list_tasks(
    ctx: Context[Any, Any, Any],
    filter: str = "all",
    parent_id: int | None = None,
) -> str:
    """Retrieve tasks with optional filtering.

    Args:
        filter: Filter tasks by completion status ('all', 'complete', or 'incomplete')
        parent_id: Filter to subtasks of a specific parent
    """
    logger.info("list_tasks called: filter=%r, parent_id=%s", filter, parent_id)
    repo = _get_repo(ctx)
    args: dict[str, Any] = {"filter": filter}
    if parent_id is not None:
        args["parent_id"] = parent_id
    result = await handle_tool_call("list_tasks", args, repo)
    return json.dumps(result, default=str)


@mcp.tool()
async def complete_task(task_id: int, ctx: Context[Any, Any, Any]) -> str:
    """Mark a task as completed.

    Args:
        task_id: The ID of the task to complete
    """
    logger.info("complete_task called: task_id=%s", task_id)
    repo = _get_repo(ctx)
    result = await handle_tool_call("complete_task", {"task_id": task_id}, repo)
    return json.dumps(result, default=str)


@mcp.tool()
async def delete_task(task_id: int, ctx: Context[Any, Any, Any]) -> str:
    """Remove a task and its subtasks.

    Args:
        task_id: The ID of the task to delete
    """
    logger.info("delete_task called: task_id=%s", task_id)
    repo = _get_repo(ctx)
    result = await handle_tool_call("delete_task", {"task_id": task_id}, repo)
    return json.dumps(result, default=str)


@mcp.tool()
async def decompose_task(
    task_id: int,
    subtask_titles: list[str],
    ctx: Context[Any, Any, Any],
) -> str:
    """Break down a complex task into subtasks. ChatGPT generates the subtask titles.

    Args:
        task_id: The ID of the task to decompose
        subtask_titles: Titles for the subtasks to create (1-10 items)
    """
    logger.info("decompose_task called: task_id=%s, subtasks=%d", task_id, len(subtask_titles))
    repo = _get_repo(ctx)
    result = await handle_tool_call(
        "decompose_task",
        {"task_id": task_id, "subtask_titles": subtask_titles},
        repo,
    )
    return json.dumps(result, default=str)


# ASGI app for `uvicorn src.server:app`
app = mcp.streamable_http_app()

if __name__ == "__main__":
    asyncio.run(mcp.run_streamable_http_async())
