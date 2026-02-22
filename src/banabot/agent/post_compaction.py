"""Post-compaction context - refresh agent context after memory compaction."""

from pathlib import Path


def get_post_compaction_context(workspace: Path) -> str | None:
    """Generate context reminder after session compaction."""
    agents_path = workspace / "AGENTS.md"
    memory_path = workspace / "MEMORY.md"

    parts = []

    if agents_path.exists():
        parts.append("- AGENTS.md (operating protocols)")

    if memory_path.exists():
        content = memory_path.read_text(encoding="utf-8")
        if content and len(content) > 20:
            parts.append("- MEMORY.md (long-term memory)")

    if not parts:
        return None

    return f"""[Post-compaction Context Refresh]

The session was compacted. Before continuing, re-familiarize yourself with:
{chr(10).join(parts)}

This ensures your operating context is restored after memory consolidation."""
