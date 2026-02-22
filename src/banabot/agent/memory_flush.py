"""Pre-compaction memory flush."""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger


async def run_memory_flush(workspace: Path, session, provider, model: str, config) -> bool:
    """Run pre-compaction memory flush before consolidation."""
    if not config.enabled or len(session.messages) < 10:
        return False

    recent = session.messages[-20:]
    conversation = []
    for m in recent:
        content = m.get("content", "")
        if content and len(content) < 500:
            conversation.append(f"{m.get('role', '?').upper()}: {content[:300]}")

    if not conversation:
        return False

    prompt = f"""Pre-compaction memory flush.
The session is about to be compacted. Save any important context to durable memory now.
Use format: memory/YYYY-MM-DD.md - if exists, APPEND new content.
If nothing important, respond with: {{"flush": false}}

Look for: user facts, technical decisions, tasks, commitments.

Conversation:
{chr(10).join(conversation[-15:])}

Respond with JSON: {{"flush": true/false, "content": "what to save"}}"""

    try:
        response = await provider.chat(messages=[{"role": "user", "content": prompt}], model=model)
        text = (response.content or "").strip()

        if '"flush": false' in text.lower() or "flush: false" in text.lower():
            return False

        try:
            data = json.loads(text)
            content = data.get("content", "")
        except Exception:
            lines = text.split("\n")
            content = "\n".join(line for line in lines if not line.strip().startswith("{")).strip()

        if not content or len(content) < 10:
            return False

        await _save_flush_memory(workspace, content)
        logger.info(f"Pre-compaction memory flush executed: {len(content)} chars")
        return True

    except Exception as e:
        logger.error(f"Memory flush failed: {e}")
        return False


async def _save_flush_memory(workspace: Path, content: str) -> None:
    """Save content to today's memory file."""
    from banabot.utils.helpers import ensure_dir

    memory_dir = ensure_dir(workspace / "memory")
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = memory_dir / f"{today}.md"

    existing = ""
    if filepath.exists():
        existing = filepath.read_text(encoding="utf-8")
        if existing:
            existing += "\n\n---\n\n"

    new_content = existing + f"## {datetime.now().strftime('%H:%M')}\n\n{content}"
    filepath.write_text(new_content, encoding="utf-8")
    logger.info(f"Flushed memory to {filepath.name}")
