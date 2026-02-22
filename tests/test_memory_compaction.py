"""Tests for memory flush and post-compaction."""

import tempfile
from pathlib import Path

import pytest


class TestPostCompaction:
    """Tests for post-compaction context."""

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_no_files_returns_none(self, workspace):
        """Test returns None when no files exist."""
        from banabot.agent.post_compaction import get_post_compaction_context

        result = get_post_compaction_context(workspace)
        assert result is None

    def test_only_agents_md(self, workspace):
        """Test returns AGENTS.md reminder when it exists."""
        from banabot.agent.post_compaction import get_post_compaction_context

        (workspace / "AGENTS.md").write_text("# Agents\n\nprotocols")

        result = get_post_compaction_context(workspace)

        assert result is not None
        assert "AGENTS.md" in result
        content = result if isinstance(result, str) else str(result)
        assert "MEMORY.md" not in content

    def test_only_memory_md_with_content(self, workspace):
        """Test returns MEMORY.md reminder when it exists with content."""
        from banabot.agent.post_compaction import get_post_compaction_context

        (workspace / "MEMORY.md").write_text("# Memory\n\nUser facts here")

        result = get_post_compaction_context(workspace)

        assert result is not None
        assert "MEMORY.md" in result

    def test_empty_memory_md_ignored(self, workspace):
        """Test empty MEMORY.md is ignored."""
        from banabot.agent.post_compaction import get_post_compaction_context

        (workspace / "AGENTS.md").write_text("# Agents")
        (workspace / "MEMORY.md").write_text("")

        result = get_post_compaction_context(workspace)

        assert result is not None
        content = result if isinstance(result, str) else str(result)
        assert "MEMORY.md" not in content

    def test_both_files_returned(self, workspace):
        """Test both files returned when they exist with content."""
        from banabot.agent.post_compaction import get_post_compaction_context

        (workspace / "AGENTS.md").write_text("# Agents")
        (workspace / "MEMORY.md").write_text("# Memory\n\nUser prefers short responses")

        result = get_post_compaction_context(workspace)

        assert result is not None
        assert "AGENTS.md" in result
        assert "MEMORY.md" in result


class TestMemoryFlush:
    """Tests for pre-compaction memory flush."""

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_save_flush_creates_file(self, workspace):
        """Test _save_flush_memory creates file."""
        from banabot.agent.memory_flush import _save_flush_memory

        await _save_flush_memory(workspace, "Important fact about user")

        memory_dir = workspace / "memory"
        files = list(memory_dir.glob("*.md"))
        assert len(files) == 1
        assert "2026" in files[0].name

    @pytest.mark.asyncio
    async def test_save_flush_appends(self, workspace):
        """Test _save_flush_memory appends to existing."""
        from banabot.agent.memory_flush import _save_flush_memory

        await _save_flush_memory(workspace, "First fact")
        await _save_flush_memory(workspace, "Second fact")

        memory_dir = workspace / "memory"
        files = list(memory_dir.glob("*.md"))
        assert len(files) == 1

        content = files[0].read_text()
        assert "First fact" in content
        assert "Second fact" in content
        assert "---" in content
