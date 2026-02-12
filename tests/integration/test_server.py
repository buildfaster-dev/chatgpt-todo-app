from src.server import mcp

EXPECTED_TOOLS = {"add_task", "list_tasks", "complete_task", "delete_task", "decompose_task"}


class TestServerConfig:
    def test_server_name(self):
        assert mcp.name == "ChatGPT ToDo App"

    def test_server_has_instructions(self):
        assert mcp.instructions is not None
        assert "tasks" in mcp.instructions.lower()


class TestToolRegistration:
    def test_all_tools_registered(self):
        tool_names = set(mcp._tool_manager._tools.keys())
        assert tool_names == EXPECTED_TOOLS

    def test_tool_count(self):
        assert len(mcp._tool_manager._tools) == 5


class TestToolSchemas:
    def _get_tool(self, name):
        return mcp._tool_manager._tools[name]

    def test_add_task_has_required_params(self):
        props = self._get_tool("add_task").parameters["properties"]
        assert "title" in props
        assert "parent_id" in props

    def test_list_tasks_has_filter_param(self):
        props = self._get_tool("list_tasks").parameters["properties"]
        assert "filter" in props
        assert "parent_id" in props

    def test_complete_task_has_task_id(self):
        props = self._get_tool("complete_task").parameters["properties"]
        assert "task_id" in props

    def test_delete_task_has_task_id(self):
        props = self._get_tool("delete_task").parameters["properties"]
        assert "task_id" in props

    def test_decompose_task_has_required_params(self):
        props = self._get_tool("decompose_task").parameters["properties"]
        assert "task_id" in props
        assert "subtask_titles" in props


class TestAsgiApp:
    def test_app_is_starlette_instance(self):
        from src.server import app
        from starlette.applications import Starlette

        assert isinstance(app, Starlette)
