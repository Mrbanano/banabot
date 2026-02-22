import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Skill:
    name: str
    description: str
    path: Path
    content: str
    frontmatter: dict
    keywords: list[str] = field(default_factory=list)
    requires: dict = field(default_factory=dict)
    available: bool = True
    emoji: str = ""


class SkillLoader:
    """Motor de skills v2 - formato XML para prompts."""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self._cache: dict[str, Skill] = {}

    def load_all(self) -> dict[str, Skill]:
        """Carga todos los skills del directorio."""
        if self._cache:
            return self._cache

        skills = {}
        for category in self._get_categories():
            category_path = self.skills_dir / category
            if not category_path.is_dir():
                continue

            for skill_path in category_path.iterdir():
                if not skill_path.is_dir():
                    continue

                skill_file = skill_path / "SKILL.md"
                if not skill_file.exists():
                    continue

                skill = self._load_skill(skill_path, skill_file)
                if skill:
                    skills[skill.name] = skill

        self._cache = skills
        return skills

    def _get_categories(self) -> list[str]:
        """Categorías de skills."""
        return ["_core", "_integrations", "_tools"]

    def _load_skill(self, path: Path, skill_file: Path) -> Optional[Skill]:
        """Carga un skill individual."""
        try:
            content = skill_file.read_text(encoding="utf-8")
        except Exception:
            return None

        frontmatter = {}
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                yaml_content = content[3:end]
                try:
                    frontmatter = yaml.safe_load(yaml_content) or {}
                except yaml.YAMLError:
                    frontmatter = {}

        name = frontmatter.get("name", path.name)
        description = frontmatter.get("description", "")

        metadata = frontmatter.get("metadata", {})
        openclaw_meta = metadata.get("openclaw", {})

        keywords = frontmatter.get("keywords", [])
        requires = openclaw_meta.get("requires", {})

        available = self._check_availability(requires)
        emoji = openclaw_meta.get("emoji", "")

        return Skill(
            name=name,
            description=description,
            path=skill_file,
            content=content,
            frontmatter=frontmatter,
            keywords=keywords,
            requires=requires,
            available=available,
            emoji=emoji,
        )

    def _check_availability(self, requires: dict) -> bool:
        """Verifica si las dependencias del skill están disponibles."""
        bins = requires.get("bins", [])
        any_bins = requires.get("anyBins", [])

        if bins:
            return all(shutil.which(b) for b in bins)
        elif any_bins:
            return any(shutil.which(b) for b in any_bins)
        return True

    def format_for_prompt(self, skills: Optional[dict[str, Skill]] = None) -> str:
        """Formatea skills para inyección en prompt (formato XML)."""
        if skills is None:
            skills = self.load_all()

        lines = ["<available_skills>"]

        for skill in skills.values():
            lines.append("  <skill>")
            lines.append(f"    <name>{skill.name}</name>")
            lines.append(f"    <description>{skill.description}</description>")
            if skill.keywords:
                lines.append(f"    <keywords>{', '.join(skill.keywords)}</keywords>")
            lines.append("  </skill>")

        lines.append("</available_skills>")
        lines.append("")
        lines.append("## Skills Usage")
        lines.append("Before replying: scan <available_skills> entries.")
        lines.append("- If 1 skill applies: read its SKILL.md, then follow it")
        lines.append("- If multiple apply: choose the most specific")
        lines.append("- If none apply: don't read any")

        return "\n".join(lines)

    def get_skill_content(self, name: str) -> Optional[str]:
        """Obtiene el contenido de un skill específico."""
        skills = self.load_all()
        skill = skills.get(name)
        return skill.content if skill else None

    def get_skill(self, name: str) -> Optional[Skill]:
        """Obtiene un skill específico."""
        skills = self.load_all()
        return skills.get(name)

    def reload(self) -> dict[str, Skill]:
        """Recarga todos los skills (invalida cache)."""
        self._cache = {}
        return self.load_all()
