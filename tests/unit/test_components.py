import pytest

from src.ui.components import (
    render_confirmation,
    render_task_card,
    render_task_hierarchy,
    render_task_list,
)


class TestRenderTaskCard:
    def test_renders_inline_card(self):
        task = {"title": "Buy milk", "completed": False}
        html = render_task_card(task)
        assert "<inline-card>" in html
        assert "</inline-card>" in html

    def test_renders_title(self):
        task = {"title": "Buy milk", "completed": False}
        html = render_task_card(task)
        assert "Buy milk" in html

    def test_escapes_html_in_title(self):
        task = {"title": "<script>alert('xss')</script>", "completed": False}
        html = render_task_card(task)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_incomplete_task_shows_circle(self):
        task = {"title": "Task", "completed": False}
        html = render_task_card(task)
        assert "○" in html

    def test_completed_task_shows_checkmark(self):
        task = {"title": "Task", "completed": True}
        html = render_task_card(task)
        assert "✓" in html

    def test_completed_task_has_completed_class(self):
        task = {"title": "Task", "completed": True}
        html = render_task_card(task)
        assert 'class="status completed"' in html

    def test_incomplete_task_has_status_class(self):
        task = {"title": "Task", "completed": False}
        html = render_task_card(task)
        assert 'class="status"' in html

    def test_includes_styles(self):
        task = {"title": "Task", "completed": False}
        html = render_task_card(task)
        assert "<style>" in html


class TestRenderTaskList:
    def test_empty_list_shows_message(self):
        html = render_task_list([])
        assert "No tasks found" in html

    def test_renders_inline_card(self):
        html = render_task_list([])
        assert "<inline-card>" in html

    def test_shows_task_count(self):
        tasks = [{"title": "A", "completed": False}, {"title": "B", "completed": False}]
        html = render_task_list(tasks)
        assert "2 task(s)" in html

    def test_renders_all_tasks(self):
        tasks = [
            {"title": "First", "completed": False},
            {"title": "Second", "completed": True},
        ]
        html = render_task_list(tasks)
        assert "First" in html
        assert "Second" in html

    def test_escapes_html_in_titles(self):
        tasks = [{"title": "<b>bold</b>", "completed": False}]
        html = render_task_list(tasks)
        assert "<b>" not in html
        assert "&lt;b&gt;" in html

    def test_shows_status_icons(self):
        tasks = [
            {"title": "Incomplete", "completed": False},
            {"title": "Complete", "completed": True},
        ]
        html = render_task_list(tasks)
        assert "○" in html
        assert "✓" in html


class TestRenderConfirmation:
    def test_renders_message(self):
        html = render_confirmation("Task deleted!")
        assert "Task deleted!" in html

    def test_renders_inline_card(self):
        html = render_confirmation("Done")
        assert "<inline-card>" in html

    def test_escapes_html_in_message(self):
        html = render_confirmation("<script>bad</script>")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_without_task(self):
        html = render_confirmation("Success")
        assert "Success" in html

    def test_with_task_shows_title(self):
        task = {"title": "My task"}
        html = render_confirmation("Completed", task=task)
        assert "My task" in html

    def test_escapes_task_title(self):
        task = {"title": "<em>styled</em>"}
        html = render_confirmation("Done", task=task)
        assert "<em>" not in html
        assert "&lt;em&gt;" in html

    def test_has_confirmation_class(self):
        html = render_confirmation("Done")
        assert 'class="confirmation"' in html


class TestRenderTaskHierarchy:
    def test_renders_parent_title(self):
        parent = {"title": "Parent task"}
        html = render_task_hierarchy(parent, [])
        assert "Parent task" in html

    def test_renders_inline_card(self):
        parent = {"title": "Parent"}
        html = render_task_hierarchy(parent, [])
        assert "<inline-card>" in html

    def test_renders_subtasks(self):
        parent = {"title": "Parent"}
        subtasks = [
            {"title": "Sub 1", "completed": False},
            {"title": "Sub 2", "completed": True},
        ]
        html = render_task_hierarchy(parent, subtasks)
        assert "Sub 1" in html
        assert "Sub 2" in html

    def test_shows_subtask_status(self):
        parent = {"title": "Parent"}
        subtasks = [
            {"title": "Incomplete", "completed": False},
            {"title": "Complete", "completed": True},
        ]
        html = render_task_hierarchy(parent, subtasks)
        assert "○" in html
        assert "✓" in html

    def test_escapes_parent_title(self):
        parent = {"title": "<div>Parent</div>"}
        html = render_task_hierarchy(parent, [])
        assert "<div>Parent</div>" not in html
        assert "&lt;div&gt;" in html

    def test_escapes_subtask_titles(self):
        parent = {"title": "Parent"}
        subtasks = [{"title": "<span>Sub</span>", "completed": False}]
        html = render_task_hierarchy(parent, subtasks)
        assert "<span>" not in html
        assert "&lt;span&gt;" in html

    def test_empty_subtasks_shows_message(self):
        parent = {"title": "Parent"}
        html = render_task_hierarchy(parent, [])
        assert "No subtasks" in html

    def test_has_hierarchy_class(self):
        parent = {"title": "Parent"}
        html = render_task_hierarchy(parent, [])
        assert 'class="hierarchy"' in html


class TestDarkModeSupport:
    def test_includes_dark_mode_media_query(self):
        task = {"title": "Task", "completed": False}
        html = render_task_card(task)
        assert "@media (prefers-color-scheme: dark)" in html

    def test_uses_css_variables(self):
        task = {"title": "Task", "completed": False}
        html = render_task_card(task)
        assert "var(--card-bg" in html
