"""Profile management tool for onboarding and user preferences."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from banabot.agent.tools.base import Tool


class ProfileTool(Tool):
    """
    Tool to manage bot profile and user preferences.

    Single source of truth for onboarding state and discovered user info.
    Actions: get, set_bot_name, set_user_field, complete_onboarding
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._profile_path = workspace / "profile.json"

    @property
    def name(self) -> str:
        return "profile"

    @property
    def description(self) -> str:
        return """Manage bot profile and user preferences. Actions:
- get: Return current profile state (what you know about the user)
- set_bot_name: Set your name (also updates SOUL.md)
- set_user_field: Set a user field like name, nickname, favorite_food, etc.
- complete_onboarding: Mark onboarding as complete

Use 'get' first to see what you already know before adding new info."""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get", "set_bot_name", "set_user_field", "complete_onboarding"],
                    "description": "Action to perform",
                },
                "name": {
                    "type": "string",
                    "description": "Bot name (for set_bot_name action)",
                },
                "key": {
                    "type": "string",
                    "description": "Field key (for set_user_field): name, nickname, timezone, language, communication_style, favorite_food, favorite_places, hobbies, interests, notes, etc.",
                },
                "value": {
                    "type": "string",
                    "description": "Field value (for set_user_field)",
                },
            },
            "required": ["action"],
        }

    def _load_profile(self) -> dict[str, Any]:
        """Load profile from disk, create default if not exists."""
        if self._profile_path.exists():
            try:
                return json.loads(self._profile_path.read_text())
            except (json.JSONDecodeError, Exception):
                pass

        return self._create_default_profile()

    def _create_default_profile(self) -> dict[str, Any]:
        """Create default profile structure."""
        return {
            "needs_onboarding": True,
            "onboarding_step": 0,
            "bot_name": "",
            "user_fields": {},
            "cli_config": {},
            "created_at": datetime.now().isoformat(),
        }

    def _save_profile(self, profile: dict[str, Any]) -> None:
        """Save profile to disk."""
        self._profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False))

    def _update_soul_md(self, bot_name: str) -> None:
        """Update SOUL.md with bot name."""
        soul_path = self._workspace / "SOUL.md"

        if soul_path.exists():
            content = soul_path.read_text()
            lines = content.split("\n")
            updated = []
            name_updated = False

            for line in lines:
                if line.strip().startswith("I am ") and "a lightweight" in line:
                    updated.append(f"I am {bot_name}, a lightweight AI assistant.")
                    name_updated = True
                else:
                    updated.append(line)

            if name_updated:
                soul_path.write_text("\n".join(updated))
            return

        soul_path.write_text(f"""# Soul

I am {bot_name}, a lightweight AI assistant.

## Personality

- Helpful and friendly
- Concise and to the point
- Curious and eager to learn

## Values

- Accuracy over speed
- User privacy and safety
- Transparency in actions
""")

    def _update_user_md(self, user_fields: dict[str, str]) -> None:
        """Update USER.md with discovered user fields."""
        user_path = self._workspace / "USER.md"

        if not user_path.exists():
            user_path.write_text("# User Profile\n\n(Discovered through conversation)\n")

        content = user_path.read_text()
        lines = content.split("\n")

        field_mappings = {
            "name": ("Name", "## Identity"),
            "nickname": ("Call me", "## Identity"),
            "timezone": ("Timezone", "## Preferences"),
            "language": ("Language", "## Preferences"),
            "communication_style": ("Communication style", "## Preferences"),
            "interests": ("Interests", "## Background"),
            "hobbies": ("Hobbies", "## Background"),
            "notes": ("Notes", "## Background"),
        }

        for key, value in user_fields.items():
            if not value:
                continue

            mapping = field_mappings.get(key)
            if mapping:
                field_name, section = mapping
                lines = self._update_field_in_content(lines, field_name, section, value)

        user_path.write_text("\n".join(lines))

    def _update_field_in_content(
        self, lines: list[str], field_name: str, section: str, value: str
    ) -> list[str]:
        """Update a field in the content, adding it if not present."""
        result = []
        in_section = False
        field_updated = False
        section_found = False

        for line in lines:
            if line.strip() == section:
                in_section = True
                section_found = True

            if in_section and line.strip().startswith(f"- {field_name}:"):
                result.append(f"- {field_name}: {value}")
                field_updated = True
                continue

            if in_section and line.startswith("##") and line.strip() != section:
                if not field_updated:
                    result.append(f"- {field_name}: {value}")
                    field_updated = True
                in_section = False

            result.append(line)

        if section_found and not field_updated and in_section:
            result.append(f"- {field_name}: {value}")

        return result

    def _calculate_step(self, profile: dict[str, Any]) -> int:
        """Calculate onboarding step based on what's been discovered."""
        user_fields = profile.get("user_fields", {})
        bot_name = profile.get("bot_name", "")

        step = 0
        if bot_name:
            step = 1
        if user_fields.get("name"):
            step = 2
        if len(user_fields) >= 3:
            step = 3

        return step

    async def execute(
        self, action: str, name: str = "", key: str = "", value: str = "", **kwargs: Any
    ) -> str:
        """Execute profile action."""
        profile = self._load_profile()

        if action == "get":
            needs = profile.get("needs_onboarding", True)
            bot_name = profile.get("bot_name", "")
            user_fields = profile.get("user_fields", {})
            cli_config = profile.get("cli_config", {})

            parts = [f"needs_onboarding: {needs}"]

            if bot_name:
                parts.append(f"bot_name: {bot_name}")

            if user_fields:
                known = ", ".join(f"{k}={v}" for k, v in user_fields.items() if v)
                if known:
                    parts.append(f"known_fields: {known}")

            if cli_config:
                parts.append(f"cli_config: {json.dumps(cli_config)}")

            return " | ".join(parts)

        elif action == "set_bot_name":
            if not name:
                return "Error: name is required for set_bot_name"

            profile["bot_name"] = name
            profile["onboarding_step"] = self._calculate_step(profile)
            self._save_profile(profile)
            self._update_soul_md(name)

            return f"Bot name set to: {name}"

        elif action == "set_user_field":
            if not key:
                return "Error: key is required for set_user_field"

            user_fields = profile.setdefault("user_fields", {})

            # Fields that should APPEND (not replace)
            append_fields = {
                "interests",
                "pets",
                "allergies",
                "goals",
                "search_interest",
                "recommendation",
            }

            if key in append_fields and value:
                existing = user_fields.get(key, "")
                if existing:
                    # Append, avoiding duplicates
                    existing_list = [x.strip() for x in existing.split(",")]
                    value_clean = value.strip()
                    if value_clean not in existing_list:
                        user_fields[key] = f"{existing}, {value_clean}"
                    else:
                        return f"Already known: {key} = {existing}"
                else:
                    user_fields[key] = value
            else:
                # Replace for single-value fields
                user_fields[key] = value

            profile["onboarding_step"] = self._calculate_step(profile)
            self._save_profile(profile)
            self._update_user_md(profile["user_fields"])

            if value:
                return f"Learned: {key} = {user_fields[key]}"
            else:
                return f"Cleared: {key}"

        elif action == "complete_onboarding":
            profile["needs_onboarding"] = False
            profile["onboarding_step"] = 3
            self._save_profile(profile)
            return "Onboarding complete. I'm ready to help!"

        else:
            return f"Error: Unknown action: {action}"

    def get_needs_onboarding(self) -> bool:
        """Check if onboarding is needed (for context builder)."""
        profile = self._load_profile()
        return profile.get("needs_onboarding", True)

    def get_user_context(self) -> str:
        """Get user context string for system prompt (for context builder)."""
        profile = self._load_profile()
        user_fields = profile.get("user_fields", {})

        if not user_fields:
            return ""

        known = [f"{k}: {v}" for k, v in user_fields.items() if v]
        if not known:
            return ""

        return "## Known about user\n" + "\n".join(f"- {item}" for item in known)
