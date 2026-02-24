"""Tests for heartbeat functionality."""

from unittest.mock import AsyncMock

import pytest

from banabot.agent.tools.heartbeat import HeartbeatTool
from banabot.heartbeat.service import HeartbeatService, _is_heartbeat_empty


class TestIsHeartbeatEmpty:
    """Tests for _is_heartbeat_empty function."""

    def test_none_returns_true(self):
        assert _is_heartbeat_empty(None) is True

    def test_empty_string_returns_true(self):
        assert _is_heartbeat_empty("") is True

    def test_empty_lines_returns_true(self):
        content = "\n\n\n"
        assert _is_heartbeat_empty(content) is True

    def test_only_headers_returns_true(self):
        content = """# Heartbeat Tasks

## Tasks

## Other
"""
        assert _is_heartbeat_empty(content) is True

    def test_html_comments_returns_true(self):
        content = """# Heartbeat Tasks

<!-- This is a comment -->

## Tasks
"""
        assert _is_heartbeat_empty(content) is True

    def test_empty_checkboxes_returns_true(self):
        content = """# Heartbeat Tasks

## Tasks

- [ ]
- [ ]
- [x]
"""
        assert _is_heartbeat_empty(content) is True

    def test_actual_task_returns_false(self):
        content = """# Heartbeat Tasks

## Tasks

- Check emails
"""
        assert _is_heartbeat_empty(content) is False

    def test_task_with_content_returns_false(self):
        content = """# Heartbeat Tasks

## Tasks

- Check news from NYT
- Review TODO.md
"""
        assert _is_heartbeat_empty(content) is False

    def test_plain_text_task_returns_true(self):
        """Plain text without bullet is NOT a task."""
        content = "Check the weather"
        assert _is_heartbeat_empty(content) is True

    def test_bullet_task_returns_false(self):
        """Bullet point is considered a task."""
        content = """# Heartbeat Tasks

## Tasks

- Check the weather
"""
        assert _is_heartbeat_empty(content) is False

    def test_asterisk_bullet_returns_false(self):
        """Asterisk bullet is detected as task."""
        content = """## Tasks

* Check emails
"""
        assert _is_heartbeat_empty(content) is False

    def test_plus_bullet_returns_false(self):
        """Plus sign bullet is detected as task."""
        content = """## Tasks

+ Do something
"""
        assert _is_heartbeat_empty(content) is False

    def test_indented_bullet_returns_false(self):
        """Indented bullet is detected as task."""
        content = """## Tasks

  - Indented task
"""
        assert _is_heartbeat_empty(content) is False

    def test_bullet_without_space_returns_false(self):
        """Bullet without space is detected as task."""
        content = """## Tasks

-Task without space
"""
        assert _is_heartbeat_empty(content) is False

    def test_checkbox_with_x_returns_false(self):
        """Checked checkbox is NOT empty (action done)."""
        content = """## Tasks

- [x] Task done
"""
        assert _is_heartbeat_empty(content) is False

    def test_empty_bullet_returns_true(self):
        """Just - or * without text is empty."""
        content = """## Tasks

-
"""
        assert _is_heartbeat_empty(content) is True

    def test_only_dashes_returns_true(self):
        """Just dashes is not a task."""
        content = """## Tasks

---
"""
        assert _is_heartbeat_empty(content) is True


class TestHeartbeatTool:
    """Tests for HeartbeatTool."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create a temp workspace with HEARTBEAT.md."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        heartbeat_file = workspace / "HEARTBEAT.md"
        heartbeat_file.write_text("""# Heartbeat Tasks

For dynamic tasks.

## Tasks

- Initial task
""")
        return workspace

    @pytest.fixture
    def tool(self, temp_workspace):
        return HeartbeatTool(workspace=temp_workspace)

    @pytest.mark.asyncio
    async def test_read_empty_file(self, tmp_path):
        """Test reading when no file exists."""
        workspace = tmp_path / "empty_ws"
        workspace.mkdir()
        tool = HeartbeatTool(workspace=workspace)
        result = await tool.execute(action="read")
        assert "No heartbeat tasks" in result

    @pytest.mark.asyncio
    async def test_read_with_tasks(self, tool):
        """Test reading tasks."""
        result = await tool.execute(action="read")
        assert "Current heartbeat tasks" in result
        assert "1." in result

    @pytest.mark.asyncio
    async def test_list_action(self, tool):
        """Test list action is same as read."""
        result_read = await tool.execute(action="read")
        result_list = await tool.execute(action="list")
        assert result_read == result_list

    @pytest.mark.asyncio
    async def test_add_task(self, tool):
        """Test adding a new task."""
        result = await tool.execute(action="add", task="New task to add")
        assert "Added heartbeat task" in result

        content = tool._file.read_text()
        assert "New task to add" in content

    @pytest.mark.asyncio
    async def test_add_empty_task_fails(self, tool):
        """Test adding empty task fails."""
        result = await tool.execute(action="add", task="")
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_remove_task(self, tool):
        """Test removing a task by line number."""
        await tool.execute(action="add", task="Task to remove")
        result = await tool.execute(action="remove", line=1)
        assert "Removed" in result

    @pytest.mark.asyncio
    async def test_remove_invalid_line_fails(self, tool):
        """Test removing invalid line fails."""
        result = await tool.execute(action="remove", line=999)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_remove_without_line_fails(self, tool):
        """Test removing without line number fails."""
        result = await tool.execute(action="remove")
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_clear_tasks(self, tool):
        """Test clearing all tasks."""
        result = await tool.execute(action="clear")
        assert "Cleared" in result


class TestHeartbeatService:
    """Tests for HeartbeatService."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        return workspace

    def test_heartbeat_file_path(self, temp_workspace):
        """Test heartbeat file is correctly located."""
        service = HeartbeatService(workspace=temp_workspace)
        assert service.heartbeat_file == temp_workspace / "HEARTBEAT.md"

    @pytest.mark.asyncio
    async def test_tick_skips_empty_file(self, temp_workspace):
        """Test that tick is skipped when file is empty."""
        service = HeartbeatService(
            workspace=temp_workspace,
            on_heartbeat=AsyncMock(),
            interval_s=60,
            enabled=True,
        )
        service.heartbeat_file.write_text("")

        await service._tick()
        assert service.on_heartbeat.call_count == 0

    @pytest.mark.asyncio
    async def test_tick_runs_when_has_content(self, temp_workspace):
        """Test that tick runs when file has content."""
        service = HeartbeatService(
            workspace=temp_workspace,
            on_heartbeat=AsyncMock(return_value="HEARTBEAT_OK"),
            interval_s=60,
            enabled=True,
        )
        service.heartbeat_file.write_text("""# Heartbeat Tasks

## Tasks

- Check something
""")

        await service._tick()
        assert service.on_heartbeat.call_count == 1

    @pytest.mark.asyncio
    async def test_tick_handles_missing_file(self, temp_workspace):
        """Test that tick handles missing file gracefully."""
        service = HeartbeatService(
            workspace=temp_workspace,
            on_heartbeat=AsyncMock(),
            interval_s=60,
            enabled=True,
        )

        await service._tick()
        assert service.on_heartbeat.call_count == 0
