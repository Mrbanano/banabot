"""Tests for session memory hook."""

import tempfile
from pathlib import Path

import pytest


class TestSessionMemoryHook:
    """Tests for session memory hook."""

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_save_session_memory_basic(self, workspace):
        """Test basic session memory save."""
        from banabot.agent.hooks.session_memory import save_session_memory

        messages = [
            {"role": "user", "content": "Hola, cómo estás?"},
            {"role": "assistant", "content": "Bien, gracias!"},
            {"role": "user", "content": "Quiero aprender Python"},
            {"role": "assistant", "content": "Python es..."},
        ]

        result = await save_session_memory(
            workspace=workspace,
            session_key="telegram:123",
            messages=messages,
            provider=None,
            model=None,
        )

        assert result is not None
        assert result.exists()
        content = result.read_text()
        assert "telegram:123" in content
        assert "4" in content

    @pytest.mark.asyncio
    async def test_save_empty_messages(self, workspace):
        """Test empty messages returns None."""
        from banabot.agent.hooks.session_memory import save_session_memory

        result = await save_session_memory(
            workspace=workspace,
            session_key="telegram:123",
            messages=[],
            provider=None,
            model=None,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_multiple_sessions_unique_files(self, workspace):
        """Test multiple sessions create unique files."""
        from banabot.agent.hooks.session_memory import save_session_memory

        messages = [
            {"role": "user", "content": "Test message"},
            {"role": "assistant", "content": "Test response"},
        ]

        results = []
        for i in range(5):
            result = await save_session_memory(
                workspace=workspace,
                session_key=f"telegram:{i}",
                messages=messages,
                provider=None,
                model=None,
            )
            results.append(result)

        assert all(r is not None for r in results)

        files = list((workspace / "memory").glob("*.md"))
        assert len(files) == 5

    def test_format_session_memory(self):
        """Test session memory formatting."""
        from banabot.agent.hooks.session_memory import _format_session_memory

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        content = _format_session_memory("test:key", messages)

        assert "# Session:" in content
        assert "**Session Key**: test:key" in content
        assert "**Messages**: 2" in content
        assert "**USER**: Hello" in content
        assert "**ASSISTANT**: Hi there!" in content

    def test_long_message_truncation(self):
        """Test long messages are truncated."""
        from banabot.agent.hooks.session_memory import _format_session_memory

        long_msg = "A" * 500
        content = _format_session_memory("test", [{"role": "user", "content": long_msg}])

        assert len(content) < 1000
        assert "..." in content
