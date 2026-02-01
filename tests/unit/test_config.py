from pathlib import Path


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("MCP_SERVER_HOST", raising=False)
    monkeypatch.delenv("MCP_SERVER_PORT", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    # Re-import to pick up cleared env vars
    import importlib
    import src.config

    importlib.reload(src.config)

    assert src.config.DATABASE_PATH == Path.home() / ".chatgpt-todo" / "tasks.db"
    assert src.config.MCP_SERVER_HOST == "localhost"
    assert src.config.MCP_SERVER_PORT == 8000
    assert src.config.LOG_LEVEL == "INFO"


def test_config_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MCP_SERVER_HOST", "0.0.0.0")
    monkeypatch.setenv("MCP_SERVER_PORT", "9000")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    import importlib
    import src.config

    importlib.reload(src.config)

    assert src.config.DATABASE_PATH == tmp_path / "test.db"
    assert src.config.MCP_SERVER_HOST == "0.0.0.0"
    assert src.config.MCP_SERVER_PORT == 9000
    assert src.config.LOG_LEVEL == "DEBUG"
