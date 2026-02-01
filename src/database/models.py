from __future__ import annotations

import aiosqlite


class TaskRepository:
    """Async repository for task CRUD operations."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        self.db = db

    async def create(self, title: str, parent_id: int | None = None) -> dict:
        """Create a new task and return it as a dict."""
        cursor = await self.db.execute(
            "INSERT INTO tasks (title, parent_id) VALUES (?, ?)",
            (title, parent_id),
        )
        await self.db.commit()
        return await self.get_by_id(cursor.lastrowid)

    async def get_all(
        self, filter: str = "all", parent_id: int | None = None
    ) -> list[dict]:
        """Return tasks matching the filter and optional parent_id."""
        clauses: list[str] = []
        params: list = []

        if filter == "complete":
            clauses.append("completed = 1")
        elif filter == "incomplete":
            clauses.append("completed = 0")

        if parent_id is not None:
            clauses.append("parent_id = ?")
            params.append(parent_id)

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM tasks{where} ORDER BY created_at"

        cursor = await self.db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_by_id(self, task_id: int) -> dict | None:
        """Return a single task by ID, or None if not found."""
        cursor = await self.db.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def update_completed(self, task_id: int, completed: bool) -> dict | None:
        """Mark a task as completed or incomplete. Returns updated task or None."""
        await self.db.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (completed, task_id),
        )
        await self.db.commit()
        return await self.get_by_id(task_id)

    async def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Returns True if a row was deleted."""
        cursor = await self.db.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )
        await self.db.commit()
        return cursor.rowcount > 0

    async def create_subtasks(
        self, parent_id: int, titles: list[str]
    ) -> list[dict]:
        """Create multiple subtasks under a parent. Returns the created subtasks."""
        subtasks = []
        for title in titles:
            subtask = await self.create(title, parent_id=parent_id)
            subtasks.append(subtask)
        return subtasks
