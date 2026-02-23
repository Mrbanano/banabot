"""Tests for semantic memory store."""

import tempfile
from pathlib import Path

import pytest


def is_fastembed_available():
    """Check if fastembed and usearch are available."""
    try:
        from fastembed import TextEmbedding  # noqa: F401
        from usearch.index import Index  # noqa: F401

        return True
    except ImportError:
        return False


class TestSemanticMemoryStore:
    """Tests for SemanticMemoryStore."""

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def store(self, workspace):
        """Create semantic memory store."""
        pytest.importorskip("fastembed", reason="fastembed not installed")
        pytest.importorskip("usearch", reason="usearch not installed")

        from banabot.agent.semantic_memory import SemanticMemoryStore
        from banabot.config.schema import SemanticMemoryConfig

        config = SemanticMemoryConfig(enabled=True)
        return SemanticMemoryStore(workspace, config)

    def test_store_creation(self, store):
        """Test store is created with correct defaults."""
        assert store.config.enabled is True
        assert store.config.model == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    def test_save_and_recall(self, store):
        """Test saving and recalling memories."""
        store.save("user went to Oaxaca", type="episodic", expires_days=30)
        store.save("user prefers short responses", type="user_profile", expires_days=None)
        store.save("banabot runs on Pi 4", type="fact", expires_days=180)

        stats = store.stats()
        assert stats["episodic"] == 1
        assert stats["user_profile"] == 1
        assert stats["fact"] == 1

    def test_recall_returns_relevant(self, store):
        """Test recall returns relevant memories."""
        store.save("user went to Oaxaca last week", type="episodic", expires_days=30)
        store.save("user prefers coffee", type="user_profile", expires_days=None)

        results = store.recall("Oaxaca trip", k=3, min_score=0.1)
        assert len(results) >= 1
        assert any("Oaxaca" in r["content"] for r in results)

    def test_idempotent_save(self, store):
        """Test saving same content doesn't duplicate."""
        store.save("same content", type="episodic", expires_days=30)

        stats1 = store.stats()
        store.save("same content", type="episodic", expires_days=30)
        stats2 = store.stats()

        assert stats1["episodic"] == stats2["episodic"]

    def test_disabled_config(self, workspace):
        """Test store with disabled config."""
        from banabot.agent.semantic_memory import SemanticMemoryStore
        from banabot.config.schema import SemanticMemoryConfig

        config = SemanticMemoryConfig(enabled=False)
        store = SemanticMemoryStore(workspace, config)

        assert store.config.enabled is False
