"""Session memory hook - saves session context on /new."""

import random
import re
from datetime import datetime
from pathlib import Path

from loguru import logger


async def save_session_memory(
    workspace: Path,
    session_key: str,
    messages: list[dict],
    provider=None,
    model: str | None = None,
) -> Path | None:
    """Save session context when /new is issued."""
    from banabot.utils.helpers import ensure_dir

    if not messages:
        logger.debug("No messages to save in session memory")
        return None

    memory_dir = ensure_dir(workspace / "memory")

    slug = await _generate_slug(messages, provider, model)
    if not slug:
        slug = f"session-{random.randint(1000, 9999)}"

    date_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    unique_suffix = random.randint(100, 999)
    filename = f"{date_str}-{slug}-{unique_suffix}.md"
    filepath = memory_dir / filename

    content = _format_session_memory(session_key, messages)

    try:
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Session memory saved to {filepath.relative_to(workspace)}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save session memory: {e}")
        return None


async def _generate_slug(messages: list[dict], provider, model: str | None = None) -> str | None:
    """Generate descriptive slug from messages using LLM."""
    if not provider or not model:
        return None

    recent = messages[-15:]
    conversation = []
    for m in recent:
        content = m.get("content", "")
        if content and len(content) < 500:
            conversation.append(f"{m.get('role', '?')}: {content[:200]}")

    if not conversation:
        return None

    prompt = f"""Generate a short descriptive slug (2-4 words, lowercase, hyphens) for this conversation.
Examples: "api-design", "bug-fix", "vendor-pitch"

Conversation:
{chr(10).join(conversation[-10:])}

Respond with ONLY the slug, no explanation."""

    try:
        response = await provider.chat(messages=[{"role": "user", "content": prompt}], model=model)
        text = (response.content or "").strip().lower()
        slug = re.sub(r"[^a-z0-9-]", "", text)[:20]
        if len(slug) >= 2:
            return slug
    except Exception as e:
        logger.debug(f"Slug generation failed: {e}")

    return None


def _format_session_memory(session_key: str, messages: list[dict]) -> str:
    """Format session messages into memory file content."""
    lines = [
        f"# Session: {datetime.now().isoformat()}",
        "",
        f"- **Session Key**: {session_key}",
        f"- **Messages**: {len(messages)}",
        "",
        "## Conversation",
        "",
    ]

    for m in messages[-20:]:
        content = m.get("content", "")
        if content:
            if len(content) > 300:
                content = content[:297] + "..."
            lines.append(f"**{m.get('role', '?').upper()}**: {content}")

    return "\n".join(lines)
