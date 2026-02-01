import os
from pathlib import Path

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", Path.home() / ".chatgpt-todo" / "tasks.db")
)

MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")

MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
