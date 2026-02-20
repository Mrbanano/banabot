import shutil
from pathlib import Path

import pytest

from banabot.agent.context import ContextBuilder


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
    """Tests for onboarding detection mechanism."""

    def test_needs_onboarding_empty_user_file(self, temp_workspace):
        """Should return True when USER.md doesn't exist."""
        cb = ContextBuilder(temp_workspace)
        assert cb.needs_onboarding() is True

    def test_needs_onboarding_with_template_markers(self, temp_workspace):
        """Should return True when USER.md has old template markers."""
        user_file = temp_workspace / "USER.md"
        user_file.write_text("""# User

Information about the user goes here.

## Preferences

- Communication style: (casual/formal)
- Timezone: (your timezone)
- Language: (your preferred language)
""")

        cb = ContextBuilder(temp_workspace)
        assert cb.needs_onboarding() is True

    def test_needs_onboarding_with_new_template(self, temp_workspace):
        """Should return True when USER.md has new template (empty fields)."""
        user_file = temp_workspace / "USER.md"
        user_file.write_text("""# User Profile

## Identity
- Name:
- Call me:
- Since:

## Preferences
- Timezone:
- Language:
- Communication style:
- Technical level:

## Background
- Interests:
- Currently working on:
- Notes:
""")

        cb = ContextBuilder(temp_workspace)
        assert cb.needs_onboarding() is True

    def test_needs_onboarding_false_when_filled(self, temp_workspace):
        """Should return False when USER.md has actual user data."""
        user_file = temp_workspace / "USER.md"
        user_file.write_text("""# User Profile

## Identity
- Name: Carlos
- Call me: Carlitos
- Since: 2026-02-20

## Preferences
- Timezone: America/Mexico_City
- Language: es
- Communication style: casual
- Technical level: intermediate

## Background
- Interests: programming
- Currently working on: automation
- Notes: Test user
""")

        cb = ContextBuilder(temp_workspace)
        assert cb.needs_onboarding() is False


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

    def test_onboarding_no_predefined_name(self, temp_workspace):
        """Instructions should NOT tell agent its own name - user decides."""
        cb = ContextBuilder(temp_workspace)
        instructions = cb._get_onboarding_instructions()

        assert "banabot" not in instructions.lower() or "banabot 🐒" not in instructions

    def test_onboarding_in_system_prompt_when_needed(self, temp_workspace):
        """System prompt should include onboarding instructions when needed."""
        cb = ContextBuilder(temp_workspace)
        prompt = cb.build_system_prompt()

        assert "First Conversation" in prompt
        assert "You Just Woke Up" in prompt

    def test_no_onboarding_in_system_prompt_when_not_needed(self, temp_workspace):
        """System prompt should NOT include onboarding when user profile is filled."""
        user_file = temp_workspace / "USER.md"
        user_file.write_text("""# User Profile

## Identity
- Name: Carlos
- Call me: Carlitos
- Since: 2026-02-20

## Preferences
- Timezone: America/Mexico_City
- Language: es
""")

        cb = ContextBuilder(temp_workspace)
        prompt = cb.build_system_prompt()

        assert "First Conversation" not in prompt


class TestOnboardingTemplates:
    """Tests for workspace templates created during onboard."""

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
