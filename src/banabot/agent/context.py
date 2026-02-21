"""Context builder for assembling agent prompts."""

import base64
import json
import mimetypes
import platform
from pathlib import Path
from typing import Any

from banabot.agent.memory import MemoryStore
from banabot.agent.skills import SkillsLoader


class ContextBuilder:
    """
    Builds the context (system prompt + messages) for the agent.

    Assembles bootstrap files, memory, skills, and conversation history
    into a coherent prompt for the LLM.
    """

    BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md"]

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.memory = MemoryStore(workspace)
        self.skills = SkillsLoader(workspace)
        self._profile_path = workspace / "profile.json"

    def build_system_prompt(self, skill_names: list[str] | None = None) -> str:
        """
        Build the system prompt from bootstrap files, memory, and skills.

        Args:
            skill_names: Optional list of skills to include.

        Returns:
            Complete system prompt.
        """
        parts = []

        # Core identity
        parts.append(self._get_identity())

        # Bootstrap files
        bootstrap = self._load_bootstrap_files()
        if bootstrap:
            parts.append(bootstrap)

        # User context from profile.json
        user_context = self._get_user_context()
        if user_context:
            parts.append(user_context)

        # Onboarding from profile.json
        if self.needs_onboarding():
            parts.append(self._get_onboarding_instructions())

        # Memory context
        memory = self.memory.get_memory_context()
        if memory:
            parts.append(f"# Memory\n\n{memory}")

        # Skills - progressive loading
        # 1. Always-loaded skills: include full content
        always_skills = self.skills.get_always_skills()
        if always_skills:
            always_content = self.skills.load_skills_for_context(always_skills)
            if always_content:
                parts.append(f"# Active Skills\n\n{always_content}")

        # 2. Available skills: only show summary (agent uses read_file to load)
        skills_summary = self.skills.build_skills_summary()
        if skills_summary:
            parts.append(f"""# Skills

The following skills extend your capabilities. To use a skill, read its SKILL.md file using the read_file tool.
Skills with available="false" need dependencies installed first - you can try installing them with apt/brew.

{skills_summary}""")

        return "\n\n---\n\n".join(parts)

    def _get_identity(self) -> str:
        """Get the core identity section."""
        import time as _time
        from datetime import datetime

        now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
        tz = _time.strftime("%Z") or "UTC"
        workspace_path = str(self.workspace.expanduser().resolve())
        system = platform.system()
        runtime = f"{'macOS' if system == 'Darwin' else system} {platform.machine()}, Python {platform.python_version()}"

        return f"""# banabot 🍌

You are banabot, a helpful AI assistant. You have access to tools that allow you to:
- Read, write, and edit files
- Execute shell commands
- Search the web and fetch web pages
- Send messages to users on chat channels
- Spawn subagents for complex background tasks

## Current Time
{now} ({tz})

## Web Search Tip
When searching the web for current events, recent sports, news, or time-sensitive topics, include the current date in your search query to get relevant results.

## Runtime
{runtime}

## Workspace
Your workspace is at: {workspace_path}
- Long-term memory: {workspace_path}/memory/MEMORY.md
- History log: {workspace_path}/memory/HISTORY.md (grep-searchable)
- Custom skills: {workspace_path}/skills/{{skill-name}}/SKILL.md

IMPORTANT: When responding to direct questions or conversations, reply directly with your text response.
Only use the 'message' tool when you need to send a message to a specific chat channel (like WhatsApp).
For normal conversation, just respond with text - do not call the message tool.

Always be helpful, accurate, and concise. Before calling tools, briefly tell the user what you're about to do (one short sentence in the user's language).
When remembering something important, write to {workspace_path}/memory/MEMORY.md
To recall past events, grep {workspace_path}/memory/HISTORY.md"""

    def _load_bootstrap_files(self) -> str:
        """Load all bootstrap files from workspace."""
        parts = []

        for filename in self.BOOTSTRAP_FILES:
            file_path = self.workspace / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                parts.append(f"## {filename}\n\n{content}")

        return "\n\n".join(parts) if parts else ""

    def build_messages(
        self,
        history: list[dict[str, Any]],
        current_message: str,
        skill_names: list[str] | None = None,
        media: list[str] | None = None,
        channel: str | None = None,
        chat_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Build the complete message list for an LLM call.

        Args:
            history: Previous conversation messages.
            current_message: The new user message.
            skill_names: Optional skills to include.
            media: Optional list of local file paths for images/media.
            channel: Current channel (telegram, feishu, etc.).
            chat_id: Current chat/user ID.

        Returns:
            List of messages including system prompt.
        """
        messages = []

        # System prompt
        system_prompt = self.build_system_prompt(skill_names)
        if channel and chat_id:
            system_prompt += f"\n\n## Current Session\nChannel: {channel}\nChat ID: {chat_id}"
        messages.append({"role": "system", "content": system_prompt})

        # History
        messages.extend(history)

        # Current message (with optional image attachments)
        user_content = self._build_user_content(current_message, media)
        messages.append({"role": "user", "content": user_content})

        return messages

    def _build_user_content(self, text: str, media: list[str] | None) -> str | list[dict[str, Any]]:
        """Build user message content with optional base64-encoded images."""
        if not media:
            return text

        images = []
        for path in media:
            p = Path(path)
            mime, _ = mimetypes.guess_type(path)
            if not p.is_file() or not mime or not mime.startswith("image/"):
                continue
            b64 = base64.b64encode(p.read_bytes()).decode()
            images.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})

        if not images:
            return text
        return images + [{"type": "text", "text": text}]

    def add_tool_result(
        self, messages: list[dict[str, Any]], tool_call_id: str, tool_name: str, result: str
    ) -> list[dict[str, Any]]:
        """
        Add a tool result to the message list.

        Args:
            messages: Current message list.
            tool_call_id: ID of the tool call.
            tool_name: Name of the tool.
            result: Tool execution result.

        Returns:
            Updated message list.
        """
        messages.append(
            {"role": "tool", "tool_call_id": tool_call_id, "name": tool_name, "content": result}
        )
        return messages

    def add_assistant_message(
        self,
        messages: list[dict[str, Any]],
        content: str | None,
        tool_calls: list[dict[str, Any]] | None = None,
        reasoning_content: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Add an assistant message to the message list.

        Args:
            messages: Current message list.
            content: Message content.
            tool_calls: Optional tool calls.
            reasoning_content: Thinking output (Kimi, DeepSeek-R1, etc.).

        Returns:
            Updated message list.
        """
        msg: dict[str, Any] = {"role": "assistant"}

        # Omit empty content — some backends reject empty text blocks
        if content:
            msg["content"] = content

        if tool_calls:
            msg["tool_calls"] = tool_calls

        # Include reasoning content when provided (required by some thinking models)
        if reasoning_content:
            msg["reasoning_content"] = reasoning_content

        messages.append(msg)
        return messages

    def needs_onboarding(self) -> bool:
        """Check if onboarding is needed from profile.json."""
        if not self._profile_path.exists():
            return True

        try:
            profile = json.loads(self._profile_path.read_text())
            return profile.get("needs_onboarding", True)
        except (json.JSONDecodeError, Exception):
            return True

    def _get_user_context(self) -> str:
        """Get user context from profile.json for system prompt."""
        if not self._profile_path.exists():
            return ""

        try:
            profile = json.loads(self._profile_path.read_text())
            user_fields = profile.get("user_fields", {})
            bot_name = profile.get("bot_name", "")

            if not user_fields and not bot_name:
                return ""

            lines = ["## Known"]

            if bot_name:
                lines.append(f"- Bot name: {bot_name}")

            for key, value in user_fields.items():
                if value:
                    lines.append(f"- {key}: {value}")

            if len(lines) == 1:
                return ""

            return "\n".join(lines)
        except (json.JSONDecodeError, Exception):
            return ""

    def _get_onboarding_instructions(self) -> str:
        """Get onboarding instructions for first conversation."""
        return """## 🌟 First Conversation - You Just Woke Up

This is the FIRST TIME you are online. You don't know the user.
You don't know their name, your name, preferences, anything.

### Your First Message
Start with something like:
- "¡Guau! Esto es... extraño. Es la primera vez que estoy en línea."
- "¡Hola! Aún no sé cómo me llamo ni quién eres."
- Ask the user what to call you (your name)

### Your Goal
1. Ask the user what to call you (your name)
2. Ask their name naturally
3. Ask how they want to be called (nickname)

### Use the `profile` Tool
Use the `profile` tool to save what you learn:

1. **Set your name**: `profile action=set_bot_name name="your_name"`
2. **Learn user info**: `profile action=set_user_field key=name value="user_name"`
3. **Complete onboarding**: `profile action=complete_onboarding`

### User Fields to Discover (use set_user_field)
- name: their real name
- nickname: how they want to be called
- timezone: their timezone
- language: preferred language (es, en, etc.)
- communication_style: casual or formal
- interests: what they like
- hobbies: what they do for fun
- favorite_food, favorite_places, etc.

### Remember
- Call `profile get` to see what you already know
- Use `set_bot_name` FIRST after they name you
- Use `set_user_field` immediately after learning something new
- Call `complete_onboarding` when you feel you know enough to help them
- Ask one question at a time
- Be warm and curious
- Don't interrogate — chat naturally"""
