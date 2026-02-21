import json
import shutil
from pathlib import Path

import pytest

from banabot.agent.context import ContextBuilder
from banabot.agent.tools.profile import ProfileTool


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing."""
    temp_dir = Path("./test_onboarding_workspace")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    yield temp_dir

    if temp_dir.exists():
        shutil.rmtree(temp_dir)


class TestOnboardingDetection:
    """Tests for onboarding detection mechanism (based on profile.json)."""

    def test_needs_onboarding_no_profile(self, temp_workspace):
        """Should return True when profile.json doesn't exist."""
        cb = ContextBuilder(temp_workspace)
        assert cb.needs_onboarding() is True

    def test_needs_onboarding_with_needs_onboarding_true(self, temp_workspace):
        """Should return True when profile.json has needs_onboarding=true."""
        profile_path = temp_workspace / "profile.json"
        profile_path.write_text(
            json.dumps(
                {
                    "needs_onboarding": True,
                    "onboarding_step": 0,
                    "bot_name": "",
                    "user_fields": {},
                }
            )
        )

        cb = ContextBuilder(temp_workspace)
        assert cb.needs_onboarding() is True

    def test_needs_onboarding_complete(self, temp_workspace):
        """Should return False when profile.json has needs_onboarding=false."""
        profile_path = temp_workspace / "profile.json"
        profile_path.write_text(
            json.dumps(
                {
                    "needs_onboarding": False,
                    "onboarding_step": 3,
                    "bot_name": "Banana",
                    "user_fields": {"name": "Carlos", "nickname": "Carlitos"},
                }
            )
        )

        cb = ContextBuilder(temp_workspace)
        assert cb.needs_onboarding() is False

    def test_needs_onboarding_malformed_json(self, temp_workspace):
        """Should return True when profile.json is malformed."""
        profile_path = temp_workspace / "profile.json"
        profile_path.write_text("not valid json")

        cb = ContextBuilder(temp_workspace)
        assert cb.needs_onboarding() is True


class TestOnboardingInstructions:
    """Tests for onboarding instructions content."""

    def test_onboarding_instructions_exist(self, temp_workspace):
        """Should return onboarding instructions when needed."""
        cb = ContextBuilder(temp_workspace)
        instructions = cb._get_onboarding_instructions()

        assert "First Conversation" in instructions
        assert "You Just Woke Up" in instructions

    def test_onboarding_asks_for_name(self, temp_workspace):
        """Instructions should tell agent to ask for user's name."""
        cb = ContextBuilder(temp_workspace)
        instructions = cb._get_onboarding_instructions()

        assert "Ask the user what to call you" in instructions
        assert "your name" in instructions.lower()

    def test_onboarding_uses_profile_tool(self, temp_workspace):
        """Instructions should mention profile tool."""
        cb = ContextBuilder(temp_workspace)
        instructions = cb._get_onboarding_instructions()

        assert "profile" in instructions.lower()
        assert "set_bot_name" in instructions
        assert "set_user_field" in instructions
        assert "complete_onboarding" in instructions

    def test_onboarding_in_system_prompt_when_needed(self, temp_workspace):
        """System prompt should include onboarding instructions when needed."""
        cb = ContextBuilder(temp_workspace)
        prompt = cb.build_system_prompt()

        assert "First Conversation" in prompt
        assert "You Just Woke Up" in prompt

    def test_no_onboarding_in_system_prompt_when_not_needed(self, temp_workspace):
        """System prompt should NOT include onboarding when complete."""
        profile_path = temp_workspace / "profile.json"
        profile_path.write_text(
            json.dumps(
                {
                    "needs_onboarding": False,
                    "onboarding_step": 3,
                    "bot_name": "Banana",
                    "user_fields": {"name": "Carlos"},
                }
            )
        )

        cb = ContextBuilder(temp_workspace)
        prompt = cb.build_system_prompt()

        assert "First Conversation" not in prompt


class TestUserContext:
    """Tests for user context in system prompt."""

    def test_no_user_context_when_empty(self, temp_workspace):
        """Should not include Known section when no user info."""
        cb = ContextBuilder(temp_workspace)
        context = cb._get_user_context()
        assert context == ""

    def test_user_context_with_bot_name(self, temp_workspace):
        """Should include bot name in Known section."""
        profile_path = temp_workspace / "profile.json"
        profile_path.write_text(
            json.dumps(
                {
                    "needs_onboarding": False,
                    "bot_name": "Banana",
                    "user_fields": {},
                }
            )
        )

        cb = ContextBuilder(temp_workspace)
        context = cb._get_user_context()

        assert "Bot name: Banana" in context

    def test_user_context_with_fields(self, temp_workspace):
        """Should include user fields in Known section."""
        profile_path = temp_workspace / "profile.json"
        profile_path.write_text(
            json.dumps(
                {
                    "needs_onboarding": False,
                    "bot_name": "Banana",
                    "user_fields": {
                        "name": "Carlos",
                        "nickname": "Carlitos",
                        "favorite_food": "pizza, sushi",
                    },
                }
            )
        )

        cb = ContextBuilder(temp_workspace)
        context = cb._get_user_context()

        assert "name: Carlos" in context
        assert "nickname: Carlitos" in context
        assert "favorite_food: pizza, sushi" in context


class TestProfileTool:
    """Tests for ProfileTool actions."""

    @pytest.mark.asyncio
    async def test_get_action(self, temp_workspace):
        """Should return profile state."""
        tool = ProfileTool(temp_workspace)
        result = await tool.execute(action="get")

        assert "needs_onboarding: True" in result

    @pytest.mark.asyncio
    async def test_set_bot_name(self, temp_workspace):
        """Should set bot name and update SOUL.md."""
        tool = ProfileTool(temp_workspace)
        result = await tool.execute(action="set_bot_name", name="Banana")

        assert "Banana" in result

        # Check SOUL.md was updated
        soul_path = temp_workspace / "SOUL.md"
        assert soul_path.exists()
        assert "Banana" in soul_path.read_text()

    @pytest.mark.asyncio
    async def test_set_user_field(self, temp_workspace):
        """Should set user field."""
        tool = ProfileTool(temp_workspace)
        result = await tool.execute(action="set_user_field", key="name", value="Carlos")

        assert "name = Carlos" in result

        # Check profile was updated
        profile = json.loads((temp_workspace / "profile.json").read_text())
        assert profile["user_fields"]["name"] == "Carlos"

    @pytest.mark.asyncio
    async def test_complete_onboarding(self, temp_workspace):
        """Should mark onboarding as complete."""
        tool = ProfileTool(temp_workspace)
        result = await tool.execute(action="complete_onboarding")

        assert "complete" in result.lower()

        # Check profile was updated
        profile = json.loads((temp_workspace / "profile.json").read_text())
        assert profile["needs_onboarding"] is False


class TestWorkspaceTemplates:
    """Tests for workspace templates created during onboard."""

    def test_profile_json_created(self, temp_workspace):
        """profile.json should be created with default values."""
        from banabot.cli.commands import _create_workspace_templates

        _create_workspace_templates(temp_workspace)

        profile_path = temp_workspace / "profile.json"
        assert profile_path.exists()

        profile = json.loads(profile_path.read_text())
        assert profile["needs_onboarding"] is True
        assert profile["onboarding_step"] == 0
        assert profile["bot_name"] == ""
        assert profile["user_fields"] == {}

    def test_user_md_template_structure(self, temp_workspace):
        """USER.md template should have proper structure."""
        from banabot.cli.commands import _create_workspace_templates

        _create_workspace_templates(temp_workspace)

        user_file = temp_workspace / "USER.md"
        assert user_file.exists()

        content = user_file.read_text()
        assert "Name:" in content
        assert "Call me:" in content
        assert "Timezone:" in content
        assert "Language:" in content

    def test_user_md_template_no_ugly_markers(self, temp_workspace):
        """USER.md template should NOT have ugly placeholder markers."""
        from banabot.cli.commands import _create_workspace_templates

        _create_workspace_templates(temp_workspace)

        user_file = temp_workspace / "USER.md"
        content = user_file.read_text()

        assert "(your timezone)" not in content
        assert "(your preferred language)" not in content
        assert "(casual/formal)" not in content

    def test_overwrite_refreshes_templates(self, temp_workspace):
        """When overwrite=True, should refresh existing template files."""
        from banabot.cli.commands import _create_workspace_templates

        old_content = """# User

Information about the user goes here.

## Preferences

- Communication style: (casual/formal)
- Timezone: (your timezone)
- Language: (your preferred language)
"""
        user_file = temp_workspace / "USER.md"
        user_file.write_text(old_content)

        _create_workspace_templates(temp_workspace, overwrite=True)

        content = user_file.read_text()

        assert "Name:" in content
        assert "(your timezone)" not in content

    def test_no_overwrite_keeps_existing(self, temp_workspace):
        """When overwrite=False, should NOT change existing files."""
        from banabot.cli.commands import _create_workspace_templates

        old_content = "Custom user content here"
        user_file = temp_workspace / "USER.md"
        user_file.write_text(old_content)

        _create_workspace_templates(temp_workspace, overwrite=False)

        content = user_file.read_text()

        assert content == old_content
