import aiosqlite
import pytest

from src.database.connection import init_db
from src.database.models import TaskRepository


@pytest.fixture
async def test_db():
    """In-memory SQLite database with schema initialized."""
    db = await aiosqlite.connect(":memory:")
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys=ON")
    await init_db(db)
    yield db
    await db.close()


@pytest.fixture
async def task_repo(test_db):
    """TaskRepository backed by the in-memory test database."""
    return TaskRepository(test_db)


@pytest.fixture
async def sample_task(task_repo):
    """A pre-created task for tests that need an existing task."""
    return await task_repo.create("Sample task")
