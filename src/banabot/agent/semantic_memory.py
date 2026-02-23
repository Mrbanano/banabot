"""Semantic memory store with vector embeddings."""

import math
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from banabot.config.schema import SemanticMemoryConfig

from banabot.utils.helpers import ensure_dir


class SemanticMemoryStore:
    """Semantic memory with fastembed + usearch vector store."""

    def __init__(
        self,
        workspace: Path,
        config: "SemanticMemoryConfig | None" = None,
    ):
        from banabot.config.schema import SemanticMemoryConfig

        self.workspace = workspace
        self.config = config or SemanticMemoryConfig()
        self.memory_dir = ensure_dir(workspace / "memory")
        self.db_path = self.memory_dir / "memory.db"
        self.index_path = self.memory_dir / "memory.usearch"

        self._model = None
        self._index = None
        self._db = None

    @property
    def is_available(self) -> bool:
        """True if fastembed and usearch are available."""
        self._ensure_ready()
        return self._model is not None

    def _ensure_ready(self) -> None:
        """Lazy load model, index, and DB."""
        if self._model is not None:
            return

        try:
            from fastembed import TextEmbedding
            from usearch.index import Index
        except ImportError:
            return

        try:
            self._model = TextEmbedding(self.config.model)
            self._index = Index(ndim=self.config.dimensions, metric="cos", dtype="f32")
            if self.index_path.exists():
                self._index.load(str(self.index_path))
            self._init_db()
        except Exception:
            self._model = None
            self._index = None

    def _init_db(self) -> None:
        """Initialize SQLite schema."""
        import sqlite3

        self._db = sqlite3.connect(str(self.db_path))
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_meta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'episodic',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT,
                source_path TEXT,
                line_start INTEGER,
                line_end INTEGER
            )
            """
        )
        self._db.commit()

    def save(
        self,
        content: str,
        type: str = "episodic",
        expires_days: int | None = 30,
        source_path: str | None = None,
        line_start: int | None = None,
        line_end: int | None = None,
    ) -> int | None:
        """Save an episode with embedding."""
        self._ensure_ready()
        if not self.is_available:
            return None
        assert self._db is not None
        assert self._model is not None
        assert self._index is not None

        existing = self._db.execute(
            "SELECT id FROM memory_meta WHERE content = ?", (content,)
        ).fetchone()
        if existing:
            return existing[0]

        expires = datetime.now().isoformat() if expires_days else None

        cursor = self._db.execute(
            """INSERT INTO memory_meta (content, type, expires_at, source_path, line_start, line_end)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (content, type, expires, source_path, line_start, line_end),
        )
        mid = cursor.lastrowid
        self._db.commit()

        vec = np.array(list(self._model.embed([content]))[0], dtype=np.float32)
        assert mid is not None
        self._index.add(mid, vec)
        self._index.save(str(self.index_path))

        return mid

    def recall(
        self,
        query: str,
        k: int = 5,
        min_score: float = 0.5,
        use_temporal_decay: bool | None = None,
        use_mmr: bool | None = None,
    ) -> list[dict]:
        """Semantic search for relevant memories."""
        self._ensure_ready()
        if not self.is_available:
            return []
        assert self._db is not None
        assert self._model is not None
        assert self._index is not None

        if self.config.query_expansion:
            query = self._expand_query(query)

        q_vec = np.array(list(self._model.embed([query]))[0], dtype=np.float32)
        matches = self._index.search(q_vec, k)

        if not len(matches):
            return []

        ids = [int(m.key) for m in matches]
        dist_map = {int(m.key): round(float(m.distance), 4) for m in matches}

        placeholders = ",".join("?" * len(ids))
        rows = self._db.execute(
            f"""SELECT id, content, type, created_at, source_path, line_start, line_end
            FROM memory_meta WHERE id IN ({placeholders})""",
            ids,
        ).fetchall()

        row_map = {r[0]: r for r in rows}
        results = []

        for i in ids:
            if i not in row_map:
                continue
            r = row_map[i]
            score = round(1 - dist_map[i], 3)

            if score < min_score:
                continue

            citation = ""
            if r[4]:
                start, end = r[5], r[6]
                citation = f"{r[4]}#{start}" if start == end else f"{r[4]}#{start}-{end}"

            results.append(
                {
                    "content": r[1],
                    "type": r[2],
                    "score": score,
                    "created_at": r[3],
                    "citation": citation,
                }
            )

        use_decay = (
            use_temporal_decay
            if use_temporal_decay is not None
            else self.config.temporal_decay_enabled
        )
        if use_decay and self.config.temporal_decay_half_life_days > 0:
            results = self._apply_temporal_decay(results)

        use_mmr_val = use_mmr if use_mmr is not None else self.config.mmr_enabled
        if use_mmr_val:
            results = self._apply_mmr(results, k=k)

        return results

    def _expand_query(self, query: str) -> str:
        """Expand query with keywords for better recall."""
        stop_words = {
            "en": {
                "the",
                "a",
                "an",
                "is",
                "are",
                "was",
                "were",
                "i",
                "you",
                "he",
                "she",
                "it",
                "we",
                "they",
                "my",
                "your",
                "his",
                "her",
                "its",
                "that",
                "this",
                "those",
                "these",
                "what",
                "which",
                "who",
                "how",
                "when",
                "where",
                "why",
                "please",
                "help",
                "find",
                "show",
                "get",
                "to",
                "for",
                "in",
                "on",
                "at",
                "by",
                "with",
                "from",
                "up",
                "about",
            },
            "es": {
                "el",
                "la",
                "los",
                "las",
                "un",
                "una",
                "es",
                "son",
                "está",
                "están",
                "yo",
                "tú",
                "él",
                "ella",
                "nosotros",
                "mi",
                "tu",
                "su",
                "que",
                "qué",
                "cómo",
                "cuándo",
                "dónde",
                "por",
                "para",
                "con",
                "sin",
                "por favor",
                "ayuda",
                "buscar",
                "mostrar",
                "traer",
                "de",
                "en",
            },
        }

        tokens = re.findall(r"\b\w+\b", query.lower())
        keywords = [
            t
            for t in tokens
            if t not in stop_words["en"] and t not in stop_words["es"] and len(t) >= 3
        ]

        if keywords:
            seen = set()
            unique = [kw for kw in keywords if not (kw in seen or seen.add(kw))]
            return f"{query} {' '.join(unique)}"
        return query

    def _apply_temporal_decay(self, results: list[dict]) -> list[dict]:
        """Apply temporal decay - recent memories get higher weight."""
        half_life = self.config.temporal_decay_half_life_days
        lambda_decay = math.log(2) / half_life
        now = datetime.now()

        for r in results:
            try:
                created = datetime.fromisoformat(r["created_at"])
                age_days = (now - created).total_seconds() / 86400
                decay = math.exp(-lambda_decay * age_days)
                r["score"] = round(r["score"] * decay, 3)
                r["decay_factor"] = round(decay, 3)
            except (ValueError, TypeError):
                r["decay_factor"] = 1.0

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _apply_mmr(self, results: list[dict], k: int = 5) -> list[dict]:
        """Apply Maximal Marginal Relevance for diversification."""
        if len(results) <= k:
            return results

        lambda_param = self.config.mmr_lambda
        selected = []
        remaining = list(results)

        def tokenize(text: str) -> set:
            return set(re.findall(r"\b\w+\b", text.lower()))

        def jaccard(a: set, b: set) -> float:
            if not a or not b:
                return 0.0
            return len(a & b) / len(a | b)

        remaining.sort(key=lambda x: x["score"], reverse=True)
        selected.append(remaining.pop(0))

        while len(selected) < k and remaining:
            best_idx = -1
            best_mmr = float("-inf")
            sel_tokens = [tokenize(s["content"]) for s in selected]

            for i, item in enumerate(remaining):
                relevance = item["score"]
                max_sim = max(jaccard(tokenize(item["content"]), st) for st in sel_tokens)
                mmr = lambda_param * relevance - (1 - lambda_param) * max_sim

                if mmr > best_mmr:
                    best_mmr = mmr
                    best_idx = i

            if best_idx >= 0:
                selected.append(remaining.pop(best_idx))
            else:
                break

        return selected

    def purge_expired(self) -> int:
        """Delete expired episodes and rebuild index."""
        self._ensure_ready()
        if not self.is_available:
            return 0
        assert self._db is not None

        now = datetime.now().isoformat()
        cursor = self._db.execute(
            "DELETE FROM memory_meta WHERE expires_at IS NOT NULL AND expires_at < ?", (now,)
        )
        self._db.commit()
        deleted = cursor.rowcount

        if deleted > 0:
            self._rebuild_index()
        return deleted

    def _rebuild_index(self) -> None:
        """Rebuild vector index from active SQLite records."""
        assert self._db is not None
        assert self._model is not None
        rows = self._db.execute("SELECT id, content FROM memory_meta").fetchall()

        self._index = None
        if self.index_path.exists():
            self.index_path.unlink()

        from usearch.index import Index

        self._index = Index(ndim=self.config.dimensions, metric="cos", dtype="f32")

        for row_id, content in rows:
            vec = np.array(list(self._model.embed([content]))[0], dtype=np.float32)
            self._index.add(row_id, vec)

        self._index.save(str(self.index_path))

    def stats(self) -> dict:
        """Get memory count by type."""
        self._ensure_ready()
        if not self.is_available:
            return {"episodic": 0, "fact": 0, "summary": 0, "user_profile": 0}
        assert self._db is not None

        rows = self._db.execute("SELECT type, COUNT(*) FROM memory_meta GROUP BY type").fetchall()
        stats = {"episodic": 0, "fact": 0, "summary": 0, "user_profile": 0}
        for type_name, count in rows:
            if type_name in stats:
                stats[type_name] = count
        return stats
