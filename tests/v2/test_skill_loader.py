"""Tests for v2 SkillLoader."""

import tempfile
from pathlib import Path

import pytest

from src.banabot.v2.skills.skill_loader import Skill, SkillLoader


class TestSkillLoader:
    """Test cases for SkillLoader."""

    @pytest.fixture
    def temp_skills_dir(self):
        """Create temporary skills directory with test skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_path = Path(tmpdir)

            # Create _core category
            core = skills_path / "_core"
            core.mkdir()

            # Create test skill with frontmatter
            (core / "test-skill").mkdir()
            (core / "test-skill" / "SKILL.md").write_text("""---
name: test-skill
description: A test skill for unit testing
keywords: [test, unit, example]
metadata:
  openclaw:
    emoji: "🧪"
    requires:
      bins: ["fake-binary"]
    install:
      - id: brew
        kind: brew
        formula: fake-binary
        bins: ["fake-binary"]
        label: "Install fake-binary"
---

# Test Skill

This is a test skill content.
""")

            # Create skill without metadata
            (core / "simple-skill").mkdir()
            (core / "simple-skill" / "SKILL.md").write_text("""# Simple Skill

Just a simple skill without frontmatter.
""")

            # Create skill with anyBins
            (core / "anybins-skill").mkdir()
            (core / "anybins-skill" / "SKILL.md").write_text("""---
name: anybins-skill
description: Skill with anyBins requirement
metadata:
  openclaw:
    requires:
      anyBins: ["cmd1", "cmd2"]
---

# AnyBins Skill

Test skill with anyBins.
""")

            # Create _integrations category
            integrations = skills_path / "_integrations"
            integrations.mkdir()
            (integrations / "integration-skill").mkdir()
            (integrations / "integration-skill" / "SKILL.md").write_text("""---
name: integration-skill
description: An integration skill
---

# Integration

Integration skill content.
""")

            # Create a directory without SKILL.md (should be ignored)
            (core / "no-skill-file").mkdir()

            yield skills_path

    def test_load_all_skills(self, temp_skills_dir):
        """Test loading all skills from directory."""
        loader = SkillLoader(temp_skills_dir)
        skills = loader.load_all()

        assert len(skills) == 4  # test-skill, simple-skill, anybins-skill, integration-skill
        assert "test-skill" in skills
        assert "simple-skill" in skills
        assert "anybins-skill" in skills
        assert "integration-skill" in skills

    def test_skill_attributes(self, temp_skills_dir):
        """Test skill has correct attributes."""
        loader = SkillLoader(temp_skills_dir)
        skills = loader.load_all()

        skill = skills["test-skill"]
        assert skill.name == "test-skill"
        assert skill.description == "A test skill for unit testing"
        assert skill.keywords == ["test", "unit", "example"]
        assert skill.emoji == "🧪"
        assert skill.path.name == "SKILL.md"

    def test_skill_without_frontmatter(self, temp_skills_dir):
        """Test skill without frontmatter uses folder name."""
        loader = SkillLoader(temp_skills_dir)
        skills = loader.load_all()

        skill = skills["simple-skill"]
        assert skill.name == "simple-skill"
        assert skill.description == ""
        assert skill.keywords == []

    def test_skill_availability_bins(self, temp_skills_dir):
        """Test skill availability with bins requirement."""
        loader = SkillLoader(temp_skills_dir)
        skills = loader.load_all()

        # fake-binary doesn't exist, so should be unavailable
        skill = skills["test-skill"]
        assert skill.available is False

    def test_skill_availability_anybins(self, temp_skills_dir):
        """Test skill availability with anyBins requirement."""
        loader = SkillLoader(temp_skills_dir)
        skills = loader.load_all()

        # Neither cmd1 nor cmd2 exist
        skill = skills["anybins-skill"]
        assert skill.available is False

    def test_format_for_prompt_xml(self, temp_skills_dir):
        """Test XML format for prompt."""
        loader = SkillLoader(temp_skills_dir)
        skills = loader.load_all()

        output = loader.format_for_prompt(skills)

        assert "<available_skills>" in output
        assert "</available_skills>" in output
        assert "<skill>" in output
        assert "<name>test-skill</name>" in output
        assert "<description>A test skill for unit testing</description>" in output
        assert "<keywords>test, unit, example</keywords>" in output

    def test_format_for_prompt_usage_guide(self, temp_skills_dir):
        """Test skills usage guide in prompt."""
        loader = SkillLoader(temp_skills_dir)
        skills = loader.load_all()

        output = loader.format_for_prompt(skills)

        assert "## ⚠️ CRITICAL: Skill Auto-Install Rule" in output
        assert "<available_skills>" in output
        assert "scan <available_skills>" in output.lower() or "skill" in output.lower()

    def test_get_skill_content(self, temp_skills_dir):
        """Test getting specific skill content."""
        loader = SkillLoader(temp_skills_dir)

        content = loader.get_skill_content("test-skill")

        assert content is not None
        assert "This is a test skill content" in content

    def test_get_skill_content_not_found(self, temp_skills_dir):
        """Test getting non-existent skill returns None."""
        loader = SkillLoader(temp_skills_dir)

        content = loader.get_skill_content("non-existent")

        assert content is None

    def test_get_skill(self, temp_skills_dir):
        """Test getting skill object."""
        loader = SkillLoader(temp_skills_dir)

        skill = loader.get_skill("test-skill")

        assert skill is not None
        assert skill.name == "test-skill"

    def test_cache_behavior(self, temp_skills_dir):
        """Test skills are cached after first load."""
        loader = SkillLoader(temp_skills_dir)

        skills1 = loader.load_all()
        skills2 = loader.load_all()

        # Should be the same object (cached)
        assert skills1 is skills2

    def test_reload(self, temp_skills_dir):
        """Test reload clears cache."""
        loader = SkillLoader(temp_skills_dir)

        skills1 = loader.load_all()
        skills2 = loader.reload()

        # Should be different object after reload
        assert skills1 is not skills2
        assert len(skills2) == 4


class TestSkillLoaderCategories:
    """Test categories functionality."""

    @pytest.fixture
    def temp_skills_dir(self):
        """Create temporary skills directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_path = Path(tmpdir)

            # Create all categories
            for cat in ["_core", "_integrations", "_tools"]:
                cat_dir = skills_path / cat
                cat_dir.mkdir()
                (cat_dir / f"{cat}-skill").mkdir()
                (cat_dir / f"{cat}-skill" / "SKILL.md").write_text(f"""---
name: {cat}-skill
description: A {cat} skill
---
# Content
""")

            yield skills_path

    def test_loads_all_categories(self, temp_skills_dir):
        """Test loads skills from all categories."""
        loader = SkillLoader(temp_skills_dir)
        skills = loader.load_all()

        assert len(skills) == 3
        # frontmatter name is used (includes category prefix)
        assert "_core-skill" in skills
        assert "_integrations-skill" in skills
        assert "_tools-skill" in skills


class TestSkillDataclass:
    """Test Skill dataclass."""

    def test_skill_creation(self):
        """Test creating a Skill instance."""
        skill = Skill(
            name="test",
            description="Test description",
            path=Path("/tmp/test/SKILL.md"),
            content="# Test",
            frontmatter={},
            keywords=["test"],
            requires={"bins": ["cmd"]},
            available=True,
            emoji="🧪",
        )

        assert skill.name == "test"
        assert skill.description == "Test description"
        assert skill.available is True
        assert skill.emoji == "🧪"
