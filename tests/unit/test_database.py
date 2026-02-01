import aiosqlite
import pytest

from src.database.connection import get_connection, init_db


# --- connection.py tests ---


class TestGetConnection:
    async def test_returns_connection(self, tmp_path):
        db = await get_connection(str(tmp_path / "test.db"))
        assert isinstance(db, aiosqlite.Connection)
        await db.close()

    async def test_row_factory_set(self, tmp_path):
        db = await get_connection(str(tmp_path / "test.db"))
        assert db.row_factory is aiosqlite.Row
        await db.close()

    async def test_foreign_keys_enabled(self, tmp_path):
        db = await get_connection(str(tmp_path / "test.db"))
        cursor = await db.execute("PRAGMA foreign_keys")
        row = await cursor.fetchone()
        assert row[0] == 1
        await db.close()

    async def test_wal_mode(self, tmp_path):
        db = await get_connection(str(tmp_path / "test.db"))
        cursor = await db.execute("PRAGMA journal_mode")
        row = await cursor.fetchone()
        assert row[0] == "wal"
        await db.close()


class TestInitDb:
    async def test_creates_tasks_table(self, test_db):
        cursor = await test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
        )
        assert await cursor.fetchone() is not None

    async def test_creates_indexes(self, test_db):
        cursor = await test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_tasks_%'"
        )
        indexes = {row[0] for row in await cursor.fetchall()}
        assert indexes == {"idx_tasks_completed", "idx_tasks_parent_id"}

    async def test_idempotent(self, test_db):
        """Calling init_db twice should not raise."""
        await init_db(test_db)


# --- TaskRepository tests ---


class TestCreate:
    async def test_create_returns_task(self, task_repo):
        task = await task_repo.create("Buy milk")
        assert task["title"] == "Buy milk"
        assert task["completed"] == 0
        assert task["parent_id"] is None
        assert task["id"] is not None
        assert task["created_at"] is not None

    async def test_create_with_parent(self, task_repo, sample_task):
        child = await task_repo.create("Subtask", parent_id=sample_task["id"])
        assert child["parent_id"] == sample_task["id"]

    async def test_create_empty_title_fails(self, task_repo):
        with pytest.raises(Exception):
            await task_repo.create("")


class TestGetById:
    async def test_existing_task(self, task_repo, sample_task):
        found = await task_repo.get_by_id(sample_task["id"])
        assert found == sample_task

    async def test_nonexistent_task(self, task_repo):
        assert await task_repo.get_by_id(9999) is None


class TestGetAll:
    async def test_empty_database(self, task_repo):
        assert await task_repo.get_all() == []

    async def test_returns_all_tasks(self, task_repo):
        await task_repo.create("Task 1")
        await task_repo.create("Task 2")
        tasks = await task_repo.get_all()
        assert len(tasks) == 2

    async def test_filter_complete(self, task_repo):
        t = await task_repo.create("Task")
        await task_repo.update_completed(t["id"], True)
        await task_repo.create("Incomplete task")

        complete = await task_repo.get_all(filter="complete")
        assert len(complete) == 1
        assert complete[0]["completed"] == 1

    async def test_filter_incomplete(self, task_repo):
        t = await task_repo.create("Task")
        await task_repo.update_completed(t["id"], True)
        await task_repo.create("Incomplete task")

        incomplete = await task_repo.get_all(filter="incomplete")
        assert len(incomplete) == 1
        assert incomplete[0]["completed"] == 0

    async def test_filter_by_parent_id(self, task_repo, sample_task):
        await task_repo.create("Child 1", parent_id=sample_task["id"])
        await task_repo.create("Child 2", parent_id=sample_task["id"])
        await task_repo.create("Orphan")

        children = await task_repo.get_all(parent_id=sample_task["id"])
        assert len(children) == 2
        assert all(c["parent_id"] == sample_task["id"] for c in children)

    async def test_filter_combined(self, task_repo, sample_task):
        c1 = await task_repo.create("Child 1", parent_id=sample_task["id"])
        await task_repo.create("Child 2", parent_id=sample_task["id"])
        await task_repo.update_completed(c1["id"], True)

        result = await task_repo.get_all(filter="complete", parent_id=sample_task["id"])
        assert len(result) == 1
        assert result[0]["id"] == c1["id"]

    async def test_ordered_by_created_at(self, task_repo):
        t1 = await task_repo.create("First")
        t2 = await task_repo.create("Second")
        tasks = await task_repo.get_all()
        assert tasks[0]["id"] == t1["id"]
        assert tasks[1]["id"] == t2["id"]


class TestUpdateCompleted:
    async def test_mark_complete(self, task_repo, sample_task):
        updated = await task_repo.update_completed(sample_task["id"], True)
        assert updated["completed"] == 1

    async def test_mark_incomplete(self, task_repo, sample_task):
        await task_repo.update_completed(sample_task["id"], True)
        updated = await task_repo.update_completed(sample_task["id"], False)
        assert updated["completed"] == 0

    async def test_nonexistent_task_returns_none(self, task_repo):
        result = await task_repo.update_completed(9999, True)
        assert result is None


class TestDelete:
    async def test_delete_existing(self, task_repo, sample_task):
        assert await task_repo.delete(sample_task["id"]) is True
        assert await task_repo.get_by_id(sample_task["id"]) is None

    async def test_delete_nonexistent(self, task_repo):
        assert await task_repo.delete(9999) is False

    async def test_cascade_deletes_subtasks(self, task_repo, sample_task):
        await task_repo.create_subtasks(sample_task["id"], ["Sub 1", "Sub 2"])
        await task_repo.delete(sample_task["id"])
        assert await task_repo.get_all() == []


class TestCreateSubtasks:
    async def test_creates_multiple(self, task_repo, sample_task):
        subs = await task_repo.create_subtasks(sample_task["id"], ["A", "B", "C"])
        assert len(subs) == 3
        assert all(s["parent_id"] == sample_task["id"] for s in subs)

    async def test_empty_list(self, task_repo, sample_task):
        subs = await task_repo.create_subtasks(sample_task["id"], [])
        assert subs == []

    async def test_subtask_titles_match(self, task_repo, sample_task):
        titles = ["Milk", "Eggs", "Bread"]
        subs = await task_repo.create_subtasks(sample_task["id"], titles)
        assert [s["title"] for s in subs] == titles
