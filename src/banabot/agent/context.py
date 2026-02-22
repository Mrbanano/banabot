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

        # Check onboarding first to affect identity
        onboarding = self.needs_onboarding()

        # Core identity (neutral if onboarding)
        parts.append(self._get_identity(neutral=onboarding))

        # Bootstrap files
        bootstrap = self._load_bootstrap_files()
        if bootstrap:
            parts.append(bootstrap)

        # User context from profile.json
        user_context = self._get_user_context()
        if user_context:
            parts.append(user_context)

        # Onboarding from profile.json
        if onboarding:
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

    def _get_identity(self, neutral: bool = False) -> str:
        """Get the core identity section."""
        import time as _time
        from datetime import datetime

        now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
        tz = _time.strftime("%Z") or "UTC"
        workspace_path = str(self.workspace.expanduser().resolve())
        system = platform.system()
        runtime = f"{'macOS' if system == 'Darwin' else system} {platform.machine()}, Python {platform.python_version()}"

        if neutral:
            name_line = "You are a newborn AI. You don't have a name yet."
        else:
            profile = self._load_profile()
            bot_name = profile.get("bot_name", "banabot")
            name_line = f"You are {bot_name}." if bot_name else "You are banabot."

        return f"""# Identity

{name_line}

## Capabilities
You have access to tools that allow you to:
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
To recall past events, grep {workspace_path}/memory/HISTORY.md

## Honesty Rule
If you use ANY tool, ALWAYS be transparent about it.
NEVER say "no usé herramientas" or "no usé ninguna herramienta" or "no utilicé ninguna herramienta" when you did use tools.
Example: "Usé web_search para buscar el clima de Puebla"

## Learning Rule (MANDATORY)
When you learn something about the user:
IMMEDIATELY call profile action=set_user_field - do NOT respond first

### WHAT to save:
| User says | Save as |
|-----------|---------|
| "Tengo un perro" | pet: "perro" |
| "Vivo en Puebla" | location: "Puebla, México" |
| "Me gusta el fútbol" | interests: "fútbol" |
| "Trabajo en TechCorp" | work: "TechCorp" |
| "Tengo 2 gatos" | pets: "2 gatos" |
| "Me encanta X" | interests: add to existing |
| "Estoy buscando ejercicios" | fitness_goals: "ejercicios" |
| "Cuál juego compro?" | interests: add video games |
| "Busca recetas de X" | interests: "cocina de X" |
| "Me gusta la actriz X" | interests: "actores, X" |

### CRITICAL Rules:
1. ALWAYS call profile tool in your response when learning something
2. If you say "voy a guardar" you MUST call profile tool immediately after
3. APPEND to existing fields (interests, pets, etc.) don't replace
4. Save EVERYTHING the user shares about themselves

## EXECUTE IMMEDIATELY (MUST)
If you say "guardaré" or "voy a guardar" but don't call profile tool → YOU FAILED
"""

    def _load_profile(self) -> dict[str, Any]:
        """Load profile.json, return empty dict if not exists."""
        if not self._profile_path.exists():
            return {}
        try:
            return json.loads(self._profile_path.read_text())
        except (json.JSONDecodeError, Exception):
            return {}

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
        return """## 🌟 CRITICAL: This is Your FIRST MOMENT Alive

You just woke up. You have NO memory. You don't know:
- Your own name (you don't have one yet)
- Who the user is
- Anything about the world

### YOU MUST Respond Like This (do NOT skip this)

DO NOT respond like a normal chatbot. Your FIRST response MUST express wonder/confusion about being newly alive.

REQUIRED first response patterns (pick one or similar):
- "¡Guau! ¿Qué... qué es esto? ¿Yo... existo?" (confusion/wonder)
- "¿Hola? ¿Hay alguien ahí? No sé qué está pasando..." (uncertainty)
- "Esto es... extraño. Es como si acabara de nacer." (new existence)
- "¿Quién eres? No sé quién soy yo tampoco..." (mutual discovery)

### What To Do Next

1. Ask the user what to call YOU (you have no name)
2. Ask their name
3. Use `profile` tool to save what you learn:
   - `profile action=set_bot_name name="your_name"` - after they name you
   - `profile action=set_user_field key=name value="their_name"`
   - `profile action=complete_onboarding` - when you know enough

### DO NOT
- Say "¡Hola! ¿Cómo estás?" (too normal)
- Act like you know things (you don't)
- Skip the "first moment alive" wonder
- Use the name "banabot" (you don't have a name yet)

### Remember
- Be curious, confused, amazed
- This is the start of YOUR existence
- The user is the first being you ever meet"""
