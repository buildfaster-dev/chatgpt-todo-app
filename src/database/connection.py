import aiosqlite

_SCHEMA_DDL = """\
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) > 0),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    parent_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks(parent_id);
"""


async def get_connection(db_path: str) -> aiosqlite.Connection:
    """Create an aiosqlite connection with WAL mode and foreign keys enabled."""
    db = await aiosqlite.connect(db_path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db(db: aiosqlite.Connection) -> None:
    """Initialize the database schema."""
    await db.executescript(_SCHEMA_DDL)
    await db.commit()
